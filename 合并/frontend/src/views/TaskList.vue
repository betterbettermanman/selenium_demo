<template>
  <div>
    <div class="toolbar">
      <a-space>
        <a-input-search
          v-model:value="keyword"
          placeholder="搜索账号/网站/课程/备注"
          style="width: 280px"
          allow-clear
          @search="handleSearch"
        />
        <a-select
          v-model:value="statusFilter"
          placeholder="状态筛选"
          style="width: 120px"
          allow-clear
          @change="handleSearch"
        >
          <a-select-option value="1">未完成</a-select-option>
          <a-select-option value="2">完成</a-select-option>
        </a-select>
      </a-space>
      <a-button type="primary" @click="openModal()">新增任务</a-button>
    </div>

    <a-table
      :columns="columns"
      :data-source="dataList"
      :loading="loading"
      :pagination="pagination"
      :scroll="{ x: 1200 }"
      row-key="id"
      @change="handleTableChange"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'status'">
          <a-space>
            <a-tag :color="record.status === '2' ? 'green' : 'orange'">
              {{ record.status === '2' ? '完成' : '未完成' }}
            </a-tag>
            <a-tag v-if="record.is_running" color="processing">执行中</a-tag>
          </a-space>
        </template>
        <template v-if="column.key === 'is_head'">
          {{ record.is_head === '1' ? '无头' : '有头' }}
        </template>
        <template v-if="column.key === 'password'">
          ******
        </template>
        <template v-if="column.key === 'action'">
          <a-space>
            <a-button
              type="link"
              size="small"
              :loading="startingTaskId === record.id"
              :disabled="record.is_running"
              @click="handleStart(record)"
            >
              启动
            </a-button>
            <a-button type="link" size="small" @click="openModal(record)">编辑</a-button>
            <a-popconfirm title="确定删除该任务吗？" @confirm="handleDelete(record.id)">
              <a-button type="link" danger size="small">删除</a-button>
            </a-popconfirm>
          </a-space>
        </template>
      </template>
    </a-table>

    <a-modal
      v-model:open="modalVisible"
      :title="editingId ? '编辑任务' : '新增任务'"
      width="520px"
      @ok="handleSubmit"
      :confirm-loading="submitting"
    >
      <a-form :model="form" layout="vertical">
        <a-form-item label="网站名称" required>
          <a-select
            v-model:value="form.website_id"
            placeholder="请先选择网站"
            show-search
            option-filter-prop="label"
            @change="handleWebsiteChange"
          >
            <a-select-option
              v-for="item in websiteOptions"
              :key="item.id"
              :value="item.id"
              :label="item.name"
            >
              {{ item.name }}
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="课程名称" required>
          <a-select
            v-model:value="form.course_id"
            placeholder="请选择课程"
            show-search
            option-filter-prop="label"
            :disabled="!form.website_id"
            :loading="courseLoading"
          >
            <a-select-option
              v-for="item in courseOptions"
              :key="item.id"
              :value="item.id"
              :label="item.name"
            >
              {{ item.name }}
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="账号" required>
          <a-input v-model:value="form.username" placeholder="请输入账号" />
        </a-form-item>
        <a-form-item label="密码" required>
          <a-input-password v-model:value="form.password" placeholder="请输入密码" />
        </a-form-item>
        <a-form-item label="浏览器无头模式">
          <a-select v-model:value="form.is_head">
            <a-select-option value="1">无头模式</a-select-option>
            <a-select-option value="0">有头模式</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="备注">
          <a-input v-model:value="form.remark" placeholder="请输入备注" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { message } from 'ant-design-vue'
import { courseApi, taskApi, websiteApi } from '../api'

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 70, fixed: 'left' },
  { title: '网站名称', dataIndex: 'website_name', key: 'website_name', width: 140 },
  { title: '课程名称', dataIndex: 'course_name', key: 'course_name', width: 140 },
  { title: '账号', dataIndex: 'username', key: 'username', width: 120 },
  { title: '密码', key: 'password', width: 80 },
  { title: '无头模式', key: 'is_head', width: 90 },
  { title: '状态', key: 'status', width: 90 },
  { title: '备注', dataIndex: 'remark', key: 'remark', width: 140, ellipsis: true },
  { title: '创建时间', dataIndex: 'create_time', key: 'create_time', width: 170 },
  { title: '操作', key: 'action', width: 200, fixed: 'right' },
]

const loading = ref(false)
const submitting = ref(false)
const courseLoading = ref(false)
const dataList = ref([])
const keyword = ref('')
const statusFilter = ref(undefined)
const modalVisible = ref(false)
const editingId = ref(null)
const websiteOptions = ref([])
const courseOptions = ref([])
const startingTaskId = ref(null)

const form = reactive({
  website_id: undefined,
  course_id: undefined,
  username: '',
  password: '',
  is_head: '1',
  remark: '',
})

const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showTotal: (total) => `共 ${total} 条`,
})

const fetchWebsites = async () => {
  const res = await websiteApi.list({ page: 1, page_size: 1000 })
  websiteOptions.value = res.data.list || []
}

const fetchCoursesByWebsite = async (websiteId, keepCourseId = undefined) => {
  if (!websiteId) {
    courseOptions.value = []
    form.course_id = undefined
    return
  }
  courseLoading.value = true
  try {
    const res = await courseApi.list({ page: 1, page_size: 1000, website_id: websiteId })
    courseOptions.value = res.data.list || []
    if (keepCourseId && courseOptions.value.some((item) => item.id === keepCourseId)) {
      form.course_id = keepCourseId
    } else if (!courseOptions.value.some((item) => item.id === form.course_id)) {
      form.course_id = undefined
    }
  } finally {
    courseLoading.value = false
  }
}

const handleWebsiteChange = (websiteId) => {
  fetchCoursesByWebsite(websiteId)
}

const fetchList = async () => {
  loading.value = true
  try {
    const res = await taskApi.list({
      page: pagination.current,
      page_size: pagination.pageSize,
      keyword: keyword.value,
      status: statusFilter.value || '',
    })
    dataList.value = res.data.list
    pagination.total = res.data.total
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  pagination.current = 1
  fetchList()
}

const handleTableChange = (pag) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  fetchList()
}

const resetForm = () => {
  form.website_id = undefined
  form.course_id = undefined
  form.username = ''
  form.password = ''
  form.is_head = '1'
  form.remark = ''
  courseOptions.value = []
}

const openModal = async (record = null) => {
  editingId.value = record?.id || null
  resetForm()
  if (record) {
    form.website_id = record.website_id || undefined
    form.username = record.username || ''
    form.password = record.password || ''
    form.is_head = record.is_head || '1'
    form.remark = record.remark || ''
    if (form.website_id) {
      await fetchCoursesByWebsite(form.website_id, record.course_id || undefined)
    }
  }
  modalVisible.value = true
}

const handleSubmit = async () => {
  if (!form.website_id) {
    message.warning('请先选择网站')
    return
  }
  if (!form.course_id) {
    message.warning('请选择课程')
    return
  }
  if (!form.username.trim()) {
    message.warning('请输入账号')
    return
  }
  if (!form.password.trim()) {
    message.warning('请输入密码')
    return
  }

  submitting.value = true
  try {
    const payload = {
      website_id: form.website_id,
      course_id: form.course_id,
      username: form.username,
      password: form.password,
      is_head: form.is_head,
      remark: form.remark,
    }
    if (editingId.value) {
      await taskApi.update(editingId.value, payload)
      message.success('更新成功')
    } else {
      await taskApi.create(payload)
      message.success('创建成功')
    }
    modalVisible.value = false
    fetchList()
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (id) => {
  await taskApi.delete(id)
  message.success('删除成功')
  fetchList()
}

const handleStart = async (record) => {
  if (record.is_running) {
    message.warning('任务正在执行中')
    return
  }
  startingTaskId.value = record.id
  try {
    const res = await taskApi.start(record.id)
    message.success(res.message || '任务已启动')
    fetchList()
  } finally {
    startingTaskId.value = null
  }
}

onMounted(() => {
  fetchWebsites()
  fetchList()
})
</script>

<style scoped>
.toolbar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
}
</style>
