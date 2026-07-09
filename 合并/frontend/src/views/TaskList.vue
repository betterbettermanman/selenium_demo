<template>
  <div>
    <div class="toolbar">
      <a-space>
        <a-input-search
          v-model:value="keyword"
          placeholder="搜索姓名/单位/账号/网站/课程/备注"
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
      :scroll="{ x: 1520 }"
      row-key="id"
      @change="handleTableChange"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'website_course'">
          <div class="stacked-cell">
            <div class="stacked-cell__primary">{{ record.website_name || '-' }}</div>
            <div class="stacked-cell__secondary">{{ record.course_name || '-' }}</div>
          </div>
        </template>
        <template v-if="column.key === 'user_info'">
          <div class="stacked-cell">
            <div class="stacked-cell__primary">{{ record.nick_name || '-' }}</div>
            <div class="stacked-cell__secondary">{{ record.organ_name || '-' }}</div>
          </div>
        </template>
        <template v-if="column.key === 'status'">
          <a-space>
            <a-tag :color="record.status === '2' ? 'green' : 'orange'">
              {{ record.status === '2' ? '完成' : '未完成' }}
            </a-tag>
            <a-tag v-if="record.waiting_sms" color="warning">待验证码</a-tag>
            <span v-else-if="record.is_running" class="running-status">
              <LoadingOutlined spin class="running-status__icon" />
              执行中
            </span>
          </a-space>
        </template>
        <template v-if="column.key === 'is_head'">
          {{ record.is_head === '1' ? '无头' : '有头' }}
        </template>
        <template v-if="column.key === 'is_charged'">
          <a-tag :color="record.is_charged === '1' ? 'success' : 'error'">
            {{ record.is_charged === '1' ? '是' : '否' }}
          </a-tag>
        </template>
        <template v-if="column.key === 'price'">
          {{ record.price != null && record.price !== '' ? `¥${record.price}` : '-' }}
        </template>
        <template v-if="column.key === 'action'">
          <a-space>
            <a-button
              type="link"
              size="small"
              :loading="startingTaskId === record.id"
              :disabled="record.is_running && !record.waiting_sms"
              @click="handleStart(record)"
            >
              启动
            </a-button>
            <a-popconfirm
              title="确定关闭该任务吗？将关闭对应浏览器并停止执行。"
              :disabled="!record.is_running"
              @confirm="handleStop(record.id)"
            >
              <a-button
                type="link"
                size="small"
                danger
                :loading="stoppingTaskId === record.id"
                :disabled="!record.is_running"
              >
                关闭
              </a-button>
            </a-popconfirm>
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
        <a-form-item label="姓名">
          <a-input v-model:value="form.nick_name" placeholder="请输入姓名（可选）" />
        </a-form-item>
        <a-form-item label="账号" required>
          <a-input v-model:value="form.username" placeholder="请输入账号" />
        </a-form-item>
        <a-form-item label="密码" required>
          <a-input-password v-model:value="form.password" placeholder="请输入密码" />
        </a-form-item>
        <a-form-item label="是否收费">
          <a-select v-model:value="form.is_charged">
            <a-select-option value="0">否</a-select-option>
            <a-select-option value="1">是</a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="价格">
          <a-input-number
            v-model:value="form.price"
            :min="0"
            :precision="0"
            :step="1"
            style="width: 100%"
            placeholder="请输入价格（可选）"
          />
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

    <a-modal
      v-model:open="smsModalVisible"
      title="提交手机验证码"
      :confirm-loading="smsSubmitting"
      ok-text="确认"
      cancel-text="取消"
      @ok="handleSubmitSms"
      @cancel="smsCode = ''"
    >
      <a-alert
        message="登录已发起，请输入手机短信验证码后继续执行任务"
        type="info"
        show-icon
        style="margin-bottom: 16px"
      />
      <a-form layout="vertical">
        <a-form-item label="手机验证码" required>
          <a-input
            v-model:value="smsCode"
            placeholder="请输入手机验证码"
            maxlength="8"
            @press-enter="handleSubmitSms"
          />
        </a-form-item>
        <a-button type="link" :loading="smsResending" @click="handleResendSms">
          重发验证码
        </a-button>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { LoadingOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import { courseApi, taskApi, websiteApi } from '../api'

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 70, fixed: 'left' },
  { title: '网站/课程', key: 'website_course', width: 200, ellipsis: true },
  { title: '姓名/单位', key: 'user_info', width: 180, ellipsis: true },
  { title: '账号', dataIndex: 'username', key: 'username', width: 120 },
  { title: '密码', dataIndex: 'password', key: 'password', width: 120, ellipsis: true },
  { title: '无头模式', key: 'is_head', width: 90 },
  { title: '是否收费', key: 'is_charged', width: 90 },
  { title: '价格', key: 'price', width: 90 },
  { title: '状态', key: 'status', width: 170 },
  { title: '备注', dataIndex: 'remark', key: 'remark', width: 140, ellipsis: true },
  { title: '创建时间', dataIndex: 'create_time', key: 'create_time', width: 170 },
  { title: '操作', key: 'action', width: 260, fixed: 'right' },
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
const stoppingTaskId = ref(null)
const smsModalVisible = ref(false)
const smsSubmitting = ref(false)
const smsResending = ref(false)
const smsCode = ref('')
const smsTaskId = ref(null)

const form = reactive({
  website_id: undefined,
  course_id: undefined,
  nick_name: '',
  username: '',
  password: '',
  is_head: '1',
  is_charged: '0',
  price: undefined,
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
  form.nick_name = ''
  form.username = ''
  form.password = ''
  form.is_head = '1'
  form.is_charged = '0'
  form.price = undefined
  form.remark = ''
  courseOptions.value = []
}

const openModal = async (record = null) => {
  editingId.value = record?.id || null
  resetForm()
  if (record) {
    form.website_id = record.website_id || undefined
    form.nick_name = record.nick_name || ''
    form.username = record.username || ''
    form.password = record.password || ''
    form.is_head = record.is_head || '1'
    form.is_charged = record.is_charged || '0'
    form.price = record.price != null && record.price !== '' ? Number(record.price) : undefined
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
  if (form.price != null && form.price < 0) {
    message.warning('价格不能为负数')
    return
  }

  submitting.value = true
  try {
    const payload = {
      website_id: form.website_id,
      course_id: form.course_id,
      nick_name: form.nick_name.trim(),
      username: form.username,
      password: form.password,
      is_head: form.is_head,
      is_charged: form.is_charged,
      price: form.price ?? '',
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

const handleStop = async (id) => {
  stoppingTaskId.value = id
  try {
    const res = await taskApi.stop(id)
    message.success(res.message || '任务已关闭')
    if (smsTaskId.value === id) {
      smsModalVisible.value = false
      smsCode.value = ''
      smsTaskId.value = null
    }
    fetchList()
  } finally {
    stoppingTaskId.value = null
  }
}

const handleDelete = async (id) => {
  await taskApi.delete(id)
  message.success('删除成功')
  fetchList()
}

const handleStart = async (record) => {
  if (record.waiting_sms) {
    smsTaskId.value = record.id
    smsCode.value = ''
    smsModalVisible.value = true
    return
  }
  if (record.is_running) {
    message.warning('任务正在执行中')
    return
  }
  startingTaskId.value = record.id
  const hideLoading = message.loading('正在启动浏览器并登录，请稍候...', 0)
  try {
    const res = await taskApi.start(record.id)
    if (res.data?.need_sms) {
      smsTaskId.value = record.id
      smsCode.value = ''
      smsModalVisible.value = true
      message.info(res.message || '请输入手机验证码')
    } else {
      message.success(res.message || '任务已启动')
    }
    fetchList()
  } catch (error) {
    await fetchList()
    const latest = dataList.value.find((item) => item.id === record.id)
    if (latest?.waiting_sms) {
      smsTaskId.value = record.id
      smsCode.value = ''
      smsModalVisible.value = true
      message.info('登录已完成，请输入手机验证码')
    } else if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      message.warning('启动耗时较长，请稍后刷新列表或再次点击启动')
    } else {
      message.error(error.response?.data?.message || error.message || '启动失败')
    }
  } finally {
    hideLoading()
    startingTaskId.value = null
  }
}

const handleSubmitSms = async () => {
  if (!smsCode.value.trim()) {
    message.warning('请输入手机验证码')
    return Promise.reject()
  }
  smsSubmitting.value = true
  try {
    const res = await taskApi.submitSmsCode(smsTaskId.value, smsCode.value.trim())
    message.success(res.message || '验证成功，任务继续执行')
    smsCode.value = ''
    fetchList()
  } catch (e) {
    return Promise.reject(e)
  } finally {
    smsSubmitting.value = false
  }
}

const handleResendSms = async () => {
  if (!smsTaskId.value) return
  smsResending.value = true
  try {
    const res = await taskApi.resendSmsCode(smsTaskId.value)
    message.success(res.message || '验证码已重发')
  } finally {
    smsResending.value = false
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

.stacked-cell__primary {
  line-height: 1.4;
}

.stacked-cell__secondary {
  color: rgba(0, 0, 0, 0.45);
  font-size: 12px;
  line-height: 1.4;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.running-status {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 0 7px;
  height: 22px;
  font-size: 12px;
  line-height: 20px;
  color: #1677ff;
  background: #e6f4ff;
  border: 1px solid #91caff;
  border-radius: 4px;
}

.running-status__icon {
  font-size: 12px;
}
</style>
