<template>
  <div>
    <div class="toolbar">
      <a-input-search
        v-model:value="keyword"
        placeholder="搜索网站编码/课程名称/课程ID/备注"
        style="width: 280px"
        allow-clear
        @search="handleSearch"
      />
      <a-button type="primary" @click="openModal()">新增课程</a-button>
    </div>

    <a-table
      :columns="columns"
      :data-source="dataList"
      :loading="loading"
      :pagination="pagination"
      :scroll="{ x: 1400 }"
      row-key="id"
      @change="handleTableChange"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'courses'">
          <template v-if="record.courses">
            <a-button type="link" size="small" class="json-preview-btn" @click="openJsonView(record.courses)">
              {{ formatJsonPreview(record.courses) }}
            </a-button>
          </template>
          <span v-else>-</span>
        </template>
        <template v-if="column.key === 'price'">
          {{ record.price != null && record.price !== '' ? `¥${record.price}` : '-' }}
        </template>
        <template v-if="column.key === 'credit_hours'">
          {{ record.credit_hours != null && record.credit_hours !== '' ? record.credit_hours : '-' }}
        </template>
        <template v-if="column.key === 'action'">
          <a-space>
            <a-button type="link" size="small" @click="openModal(record)">编辑</a-button>
            <a-popconfirm title="确定删除该课程吗？" @confirm="handleDelete(record.id)">
              <a-button type="link" danger size="small">删除</a-button>
            </a-popconfirm>
          </a-space>
        </template>
      </template>
    </a-table>

    <a-modal
      v-model:open="modalVisible"
      :title="editingId ? '编辑课程' : '新增课程'"
      width="640px"
      @ok="handleSubmit"
      :confirm-loading="submitting"
    >
      <a-form :model="form" layout="vertical">
        <a-form-item label="网站编码" required>
          <a-select
            v-model:value="form.website_code"
            placeholder="请先选择网站编码"
            allow-clear
            show-search
            option-filter-prop="label"
            :filter-option="filterWebsite"
          >
            <a-select-option
              v-for="item in websiteOptions"
              :key="item.code"
              :value="item.code"
              :label="item.name"
            >
              {{ item.name }}（{{ item.code }}）
            </a-select-option>
          </a-select>
        </a-form-item>
        <a-form-item label="课程名称" required>
          <a-input v-model:value="form.name" placeholder="请输入课程名称" />
        </a-form-item>
        <a-form-item label="课程ID">
          <a-input v-model:value="form.class_id" placeholder="请输入课程ID" />
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
        <a-form-item label="学时">
          <a-input-number
            v-model:value="form.credit_hours"
            :min="0"
            :precision="1"
            :step="0.5"
            style="width: 100%"
            placeholder="请输入学时（可选）"
          />
        </a-form-item>
        <a-form-item
          label="特定课表 (JSON)"
          :validate-status="coursesJsonError ? 'error' : coursesJsonValid ? 'success' : ''"
          :help="coursesJsonError || '须为合法 JSON 对象或数组，留空表示无课表'"
        >
          <div class="json-editor-toolbar">
            <a-space>
              <a-button size="small" @click="handleFormatCoursesJson">格式化</a-button>
              <a-button size="small" @click="handleValidateCoursesJson">校验</a-button>
              <a-button size="small" @click="form.coursesText = ''">清空</a-button>
            </a-space>
          </div>
          <a-textarea
            v-model:value="form.coursesText"
            :rows="8"
            class="json-textarea"
            placeholder='例如: ["课程1", "课程2"] 或 {"chapter1": ["视频1"]}'
            @blur="handleValidateCoursesJson"
            @input="handleCoursesJsonInput"
          />
        </a-form-item>
        <a-form-item label="备注">
          <a-input v-model:value="form.remark" placeholder="请输入备注" />
        </a-form-item>
      </a-form>
    </a-modal>

    <a-modal
      v-model:open="jsonViewVisible"
      title="特定课表"
      width="720px"
      :footer="null"
    >
      <pre class="json-viewer">{{ jsonViewContent }}</pre>
    </a-modal>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { message } from 'ant-design-vue'
import { courseApi, websiteApi } from '../api'
import {
  formatJsonDisplay,
  formatJsonPreview,
  parseJsonStrict,
  validateJsonText,
} from '../utils/jsonHelper'

const columns = [
  { title: '网站名称', dataIndex: 'website_name', key: 'website_name', width: 140, fixed: 'left' },
  { title: '网站编码', dataIndex: 'website_code', key: 'website_code', width: 120 },
  { title: '课程名称', dataIndex: 'name', key: 'name' },
  { title: '课程ID', dataIndex: 'class_id', key: 'class_id', width: 120 },
  { title: '价格', key: 'price', width: 90 },
  { title: '学时', key: 'credit_hours', width: 90 },
  { title: '特定课表', dataIndex: 'courses', key: 'courses', width: 220 },
  { title: '备注', dataIndex: 'remark', key: 'remark' },
  { title: '创建时间', dataIndex: 'create_time', key: 'create_time', width: 180 },
  { title: '操作', key: 'action', width: 150 },
]

const loading = ref(false)
const submitting = ref(false)
const dataList = ref([])
const keyword = ref('')
const modalVisible = ref(false)
const editingId = ref(null)
const websiteOptions = ref([])
const coursesJsonError = ref('')
const coursesJsonValid = ref(false)
const jsonViewVisible = ref(false)
const jsonViewContent = ref('')
const form = reactive({
  name: '',
  class_id: '',
  website_code: undefined,
  coursesText: '',
  price: undefined,
  credit_hours: undefined,
  remark: '',
})

const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showTotal: (total) => `共 ${total} 条`,
})

const resetCoursesJsonStatus = () => {
  coursesJsonError.value = ''
  coursesJsonValid.value = false
}

const handleCoursesJsonInput = () => {
  if (!form.coursesText.trim()) {
    resetCoursesJsonStatus()
    return
  }
  const result = validateJsonText(form.coursesText, '特定课表')
  coursesJsonError.value = result.valid ? '' : result.error
  coursesJsonValid.value = result.valid
}

const handleValidateCoursesJson = (silent = false) => {
  const result = validateJsonText(form.coursesText, '特定课表')
  coursesJsonError.value = result.valid ? '' : result.error
  coursesJsonValid.value = result.valid
  if (!silent) {
    if (result.valid) {
      if (form.coursesText.trim()) {
        message.success('JSON 格式正确')
      }
    } else {
      message.error(result.error)
    }
  }
  return result
}

const handleFormatCoursesJson = () => {
  const result = validateJsonText(form.coursesText, '特定课表')
  if (!result.valid) {
    coursesJsonError.value = result.error
    coursesJsonValid.value = false
    message.error(result.error)
    return
  }
  form.coursesText = result.formatted
  coursesJsonError.value = ''
  coursesJsonValid.value = !!form.coursesText.trim()
  if (form.coursesText.trim()) {
    message.success('已格式化')
  }
}

const openJsonView = (value) => {
  jsonViewContent.value = formatJsonDisplay(value)
  jsonViewVisible.value = true
}

const filterWebsite = (input, option) => {
  const label = option.label || ''
  const value = option.value || ''
  const kw = input.toLowerCase()
  return label.toLowerCase().includes(kw) || String(value).toLowerCase().includes(kw)
}

const fetchWebsites = async () => {
  const res = await websiteApi.list({ page: 1, page_size: 1000 })
  websiteOptions.value = (res.data.list || []).filter((item) => item.code)
}

const fetchList = async () => {
  loading.value = true
  try {
    const res = await courseApi.list({
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
  form.website_code = record?.website_code || undefined
  form.name = record?.name || ''
  form.class_id = record?.class_id || ''
  form.price = record?.price != null && record?.price !== '' ? Number(record.price) : undefined
  form.credit_hours = record?.credit_hours != null && record?.credit_hours !== ''
    ? Number(record.credit_hours)
    : undefined
  form.coursesText = record?.courses ? formatJsonDisplay(record.courses) : ''
  form.remark = record?.remark || ''
  resetCoursesJsonStatus()
  if (form.coursesText.trim()) {
    coursesJsonValid.value = true
  }
  modalVisible.value = true
}

const handleSubmit = async () => {
  if (!form.website_code) {
    message.warning('请先选择网站编码')
    return
  }
  if (!form.name.trim()) {
    message.warning('请输入课程名称')
    return
  }
  if (form.price != null && form.price < 0) {
    message.warning('价格不能为负数')
    return
  }
  if (form.credit_hours != null && form.credit_hours < 0) {
    message.warning('学时不能为负数')
    return
  }

  const jsonResult = handleValidateCoursesJson(true)
  if (!jsonResult.valid) {
    message.error(jsonResult.error)
    return
  }

  submitting.value = true
  try {
    const courses = parseJsonStrict(form.coursesText, '特定课表')
    const payload = {
      name: form.name,
      class_id: form.class_id,
      website_code: form.website_code || null,
      courses,
      price: form.price ?? '',
      credit_hours: form.credit_hours ?? '',
      remark: form.remark,
    }
    if (editingId.value) {
      await courseApi.update(editingId.value, payload)
      message.success('更新成功')
    } else {
      await courseApi.create(payload)
      message.success('创建成功')
    }
    modalVisible.value = false
    fetchList()
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (id) => {
  await courseApi.delete(id)
  message.success('删除成功')
  fetchList()
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

.json-editor-toolbar {
  margin-bottom: 8px;
}

.json-textarea {
  font-family: Consolas, Monaco, 'Courier New', monospace;
  font-size: 13px;
}

.json-preview-btn {
  padding: 0;
  height: auto;
  max-width: 200px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  text-align: left;
}

.json-viewer {
  margin: 0;
  padding: 12px;
  background: #f6f8fa;
  border-radius: 6px;
  max-height: 480px;
  overflow: auto;
  font-family: Consolas, Monaco, 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>
