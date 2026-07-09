<template>
  <div>
    <div class="toolbar">
      <a-space>
        <a-input-search
          v-model:value="keyword"
          placeholder="搜索姓名/单位/账号/网站"
          style="width: 280px"
          allow-clear
          @search="handleSearch"
        />
        <a-select
          v-model:value="websiteFilter"
          placeholder="网站筛选"
          style="width: 160px"
          allow-clear
          show-search
          option-filter-prop="label"
          @change="handleSearch"
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
      </a-space>
      <a-button type="primary" @click="openModal()">新增用户</a-button>
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
        <template v-if="column.key === 'user_info'">
          <div class="stacked-cell">
            <div class="stacked-cell__primary">{{ record.nick_name || '-' }}</div>
            <div class="stacked-cell__secondary">{{ record.organ_name || '-' }}</div>
          </div>
        </template>
        <template v-if="column.key === 'action'">
          <a-space>
            <a-button type="link" size="small" @click="handleCopy(record)">复制</a-button>
            <a-button type="link" size="small" @click="openModal(record)">编辑</a-button>
            <a-popconfirm title="确定删除该用户吗？" @confirm="handleDelete(record.id)">
              <a-button type="link" danger size="small">删除</a-button>
            </a-popconfirm>
          </a-space>
        </template>
      </template>
    </a-table>

    <a-modal
      v-model:open="modalVisible"
      :title="editingId ? '编辑用户' : '新增用户'"
      width="520px"
      @ok="handleSubmit"
      :confirm-loading="submitting"
    >
      <a-form :model="form" layout="vertical">
        <a-form-item label="网站" required>
          <a-select
            v-model:value="form.website_id"
            placeholder="请选择网站"
            show-search
            option-filter-prop="label"
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
        <a-form-item label="姓名">
          <a-input v-model:value="form.nick_name" placeholder="请输入姓名（可选）" />
        </a-form-item>
        <a-form-item label="单位名称">
          <a-input v-model:value="form.organ_name" placeholder="请输入单位名称（可选）" />
        </a-form-item>
        <a-form-item label="账号" required>
          <a-input v-model:value="form.username" placeholder="请输入账号" />
        </a-form-item>
        <a-form-item label="密码" required>
          <a-input-password v-model:value="form.password" placeholder="请输入密码" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { message } from 'ant-design-vue'
import { userAccountApi, websiteApi } from '../api'

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 70, fixed: 'left' },
  { title: '网站名称', dataIndex: 'website_name', key: 'website_name', width: 160, ellipsis: true },
  { title: '姓名/单位', key: 'user_info', width: 200, ellipsis: true },
  { title: '账号', dataIndex: 'username', key: 'username', width: 140 },
  { title: '密码', dataIndex: 'password', key: 'password', width: 140, ellipsis: true },
  { title: '创建时间', dataIndex: 'create_time', key: 'create_time', width: 170 },
  { title: '操作', key: 'action', width: 180, fixed: 'right' },
]

const loading = ref(false)
const submitting = ref(false)
const dataList = ref([])
const keyword = ref('')
const websiteFilter = ref(undefined)
const websiteOptions = ref([])
const modalVisible = ref(false)
const editingId = ref(null)

const form = reactive({
  website_id: undefined,
  nick_name: '',
  organ_name: '',
  username: '',
  password: '',
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

const fetchList = async () => {
  loading.value = true
  try {
    const res = await userAccountApi.list({
      page: pagination.current,
      page_size: pagination.pageSize,
      keyword: keyword.value,
      website_id: websiteFilter.value || undefined,
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
  form.nick_name = ''
  form.organ_name = ''
  form.username = ''
  form.password = ''
}

const openModal = (record = null) => {
  editingId.value = record?.id || null
  resetForm()
  if (record) {
    form.website_id = record.website_id || undefined
    form.nick_name = record.nick_name || ''
    form.organ_name = record.organ_name || ''
    form.username = record.username || ''
    form.password = record.password || ''
  }
  modalVisible.value = true
}

const handleSubmit = async () => {
  if (!form.website_id) {
    message.warning('请选择网站')
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
      nick_name: form.nick_name.trim(),
      organ_name: form.organ_name.trim(),
      username: form.username,
      password: form.password,
    }
    if (editingId.value) {
      await userAccountApi.update(editingId.value, payload)
      message.success('更新成功')
    } else {
      await userAccountApi.create(payload)
      message.success('创建成功')
    }
    modalVisible.value = false
    fetchList()
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (id) => {
  await userAccountApi.delete(id)
  message.success('删除成功')
  fetchList()
}

const formatAccountInfo = (record) => [
  `网站名称：${record.website_name || ''}`,
  `网址：${record.website_url || ''}`,
  `名称：${record.nick_name || ''}`,
  `账号：${record.username || ''}`,
  `密码：${record.password || ''}`,
].join('\n')

const handleCopy = async (record) => {
  const text = formatAccountInfo(record)
  try {
    await navigator.clipboard.writeText(text)
    message.success('已复制到剪贴板')
  } catch {
    const textarea = document.createElement('textarea')
    textarea.value = text
    textarea.style.position = 'fixed'
    textarea.style.opacity = '0'
    document.body.appendChild(textarea)
    textarea.select()
    try {
      document.execCommand('copy')
      message.success('已复制到剪贴板')
    } catch {
      message.error('复制失败，请手动复制')
    } finally {
      document.body.removeChild(textarea)
    }
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
</style>
