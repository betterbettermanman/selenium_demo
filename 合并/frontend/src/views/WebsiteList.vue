<template>
  <div>
    <div class="toolbar">
      <a-input-search
        v-model:value="keyword"
        placeholder="搜索网站名称/编码/URL/备注"
        style="width: 280px"
        allow-clear
        @search="handleSearch"
      />
      <a-button type="primary" @click="openModal()">新增网站</a-button>
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
        <template v-if="column.key === 'url'">
          <a
            v-if="record.url"
            :href="record.url"
            target="_blank"
            rel="noopener noreferrer"
            class="url-link"
          >
            {{ record.url }}
          </a>
          <span v-else>-</span>
        </template>
        <template v-if="column.key === 'enable_sms_code'">
          <a-tag :color="record.enable_sms_code === '1' ? 'green' : 'default'">
            {{ record.enable_sms_code === '1' ? '启用' : '不启用' }}
          </a-tag>
        </template>
        <template v-if="column.key === 'action'">
          <a-space>
            <a-button
              type="link"
              size="small"
              :loading="openingId === record.id"
              :disabled="!record.url"
              @click="handleOpenBrowser(record)"
            >
              打开网站
            </a-button>
            <a-button type="link" size="small" @click="openModal(record)">编辑</a-button>
            <a-popconfirm title="确定删除该网站吗？" @confirm="handleDelete(record.id)">
              <a-button type="link" danger size="small">删除</a-button>
            </a-popconfirm>
          </a-space>
        </template>
      </template>
    </a-table>

    <a-modal
      v-model:open="modalVisible"
      :title="editingId ? '编辑网站' : '新增网站'"
      width="560px"
      @ok="handleSubmit"
      :confirm-loading="submitting"
    >
      <a-form :model="form" layout="vertical">
        <a-form-item label="网站名称" required>
          <a-input v-model:value="form.name" placeholder="请输入网站名称" />
        </a-form-item>
        <a-form-item label="网站编码">
          <a-input v-model:value="form.code" placeholder="请输入网站编码" />
        </a-form-item>
        <a-form-item label="网站 URL">
          <a-input v-model:value="form.url" placeholder="https://example.com" />
        </a-form-item>
        <a-form-item label="是否启用手机验证码">
          <a-select v-model:value="form.enable_sms_code">
            <a-select-option value="1">启用</a-select-option>
            <a-select-option value="0">不启用</a-select-option>
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
import { websiteApi } from '../api'

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 70, fixed: 'left' },
  { title: '网站名称', dataIndex: 'name', key: 'name', width: 140 },
  { title: '网站编码', dataIndex: 'code', key: 'code', width: 100 },
  { title: '网站 URL', key: 'url', width: 220, ellipsis: true },
  { title: '手机验证码', key: 'enable_sms_code', width: 100 },
  { title: '备注', dataIndex: 'remark', key: 'remark', width: 140, ellipsis: true },
  { title: '创建时间', dataIndex: 'create_time', key: 'create_time', width: 170 },
  { title: '操作', key: 'action', width: 220, fixed: 'right' },
]

const loading = ref(false)
const submitting = ref(false)
const openingId = ref(null)
const dataList = ref([])
const keyword = ref('')
const modalVisible = ref(false)
const editingId = ref(null)
const form = reactive({ name: '', code: '', url: '', enable_sms_code: '0', remark: '' })

const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showTotal: (total) => `共 ${total} 条`,
})

const fetchList = async () => {
  loading.value = true
  try {
    const res = await websiteApi.list({
      page: pagination.current,
      page_size: pagination.pageSize,
      keyword: keyword.value,
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

const openModal = (record = null) => {
  editingId.value = record?.id || null
  form.name = record?.name || ''
  form.code = record?.code || ''
  form.url = record?.url || ''
  form.enable_sms_code = record?.enable_sms_code || '0'
  form.remark = record?.remark || ''
  modalVisible.value = true
}

const handleSubmit = async () => {
  if (!form.name.trim()) {
    message.warning('请输入网站名称')
    return
  }
  submitting.value = true
  try {
    const payload = {
      ...form,
      url: form.url.trim(),
    }
    if (editingId.value) {
      await websiteApi.update(editingId.value, payload)
      message.success('更新成功')
    } else {
      await websiteApi.create(payload)
      message.success('创建成功')
    }
    modalVisible.value = false
    fetchList()
  } finally {
    submitting.value = false
  }
}

const handleOpenBrowser = async (record) => {
  if (!record.url) {
    message.warning('请先配置网站 URL')
    return
  }
  openingId.value = record.id
  try {
    const res = await websiteApi.openBrowser(record.id)
    message.success(res.message || '浏览器已打开')
    fetchList()
  } finally {
    openingId.value = null
  }
}

const handleDelete = async (id) => {
  await websiteApi.delete(id)
  message.success('删除成功')
  fetchList()
}

onMounted(fetchList)
</script>

<style scoped>
.toolbar {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
}

.url-link {
  word-break: break-all;
}
</style>
