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
        <a-select
          v-model:value="scheduleFilter"
          placeholder="调度模式"
          style="width: 120px"
          allow-clear
          @change="handleSearch"
        >
          <a-select-option value="manual">手动</a-select-option>
          <a-select-option value="daily">每日</a-select-option>
          <a-select-option value="monthly">每月</a-select-option>
        </a-select>
      </a-space>
      <a-space>
        <a-button :loading="schedulerRunning === 'daily'" @click="handleRunSchedule('daily')">
          立即执行每日
        </a-button>
        <a-button :loading="schedulerRunning === 'monthly'" @click="handleRunSchedule('monthly')">
          立即执行每月
        </a-button>
        <a-button @click="openSchedulerModal">调度设置</a-button>
        <a-button :loading="exporting" @click="handleExport">导出</a-button>
        <a-button type="primary" @click="openModal()">新增任务</a-button>
      </a-space>
    </div>

    <a-table
      class="task-table"
      size="small"
      :columns="columns"
      :data-source="dataList"
      :loading="loading"
      :pagination="pagination"
      :scroll="{ x: 1590 }"
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
        <template v-if="column.key === 'time_info'">
          <div class="stacked-cell">
            <div class="stacked-cell__primary">{{ record.create_time || '-' }}</div>
            <div class="stacked-cell__secondary">{{ record.completed_time || '-' }}</div>
          </div>
        </template>
        <template v-if="column.key === 'progress'">
          {{ record.progress || '-' }}
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
        <template v-if="column.key === 'schedule_type'">
          {{ scheduleTypeLabel(record.schedule_type) }}
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
              :disabled="!canManualStart(record)"
              :title="manualStartTip(record)"
              @click="handleStart(record)"
            >
              启动
            </a-button>
            <a-button
              type="link"
              size="small"
              :loading="openingBrowserId === record.id"
              :disabled="record.is_running"
              @click="handleOpenBrowser(record)"
            >
              打开页面
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
      width="720px"
      @ok="handleSubmit"
      :confirm-loading="submitting"
    >
      <a-form :model="form" layout="vertical" class="task-form">
        <a-row :gutter="16">
          <a-col :span="12">
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
          </a-col>
          <a-col :span="12">
            <a-form-item label="课程名称" required>
              <a-select
                v-model:value="form.course_id"
                placeholder="请选择课程"
                show-search
                option-filter-prop="label"
                :disabled="!form.website_id"
                :loading="courseLoading"
                @change="handleCourseChange"
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
          </a-col>
          <a-col :span="12">
            <a-form-item label="姓名">
              <a-input
                v-model:value="form.nick_name"
                placeholder="请先选网站，再输入姓名可匹配已有用户"
                :disabled="!form.website_id"
                allow-clear
                @update:value="onNickNameInput"
              />
              <div v-if="userSuggestLoading" class="user-suggest-tip">正在匹配用户…</div>
              <div v-else-if="userSuggestOptions.length" class="user-suggest">
                <div class="user-suggest__tip">匹配到已有用户，点击填入账号密码</div>
                <button
                  v-for="opt in userSuggestOptions"
                  :key="opt.value"
                  type="button"
                  class="user-suggest__item"
                  @click="handleSelectUserAccount(opt.value, opt)"
                >
                  {{ opt.label }}
                </button>
              </div>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="单位">
              <a-input
                v-model:value="form.organ_name"
                placeholder="请输入单位名称（可选）"
                allow-clear
              />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="账号" required>
              <a-input v-model:value="form.username" placeholder="请输入账号" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="密码" required>
              <a-input v-model:value="form.password" placeholder="请输入密码" />
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="收费">
              <a-select v-model:value="form.is_charged">
                <a-select-option value="0">否</a-select-option>
                <a-select-option value="1">是</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
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
          </a-col>
          <a-col :span="12">
            <a-form-item label="模式">
              <a-select v-model:value="form.is_head">
                <a-select-option value="1">无头</a-select-option>
                <a-select-option value="0">有头</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="12">
            <a-form-item label="调度方式">
              <a-select v-model:value="form.schedule_type">
                <a-select-option value="manual">手动（可点启动）</a-select-option>
                <a-select-option value="daily">每日（仅定时）</a-select-option>
                <a-select-option value="monthly">每月（仅定时）</a-select-option>
              </a-select>
            </a-form-item>
          </a-col>
          <a-col :span="24">
            <a-form-item label="备注">
              <a-input v-model:value="form.remark" placeholder="请输入备注" />
            </a-form-item>
          </a-col>
        </a-row>
      </a-form>
    </a-modal>

    <a-modal
      v-model:open="schedulerModalVisible"
      title="调度设置"
      @ok="handleSaveScheduler"
      :confirm-loading="schedulerSaving"
    >
      <a-form layout="vertical">
        <a-form-item label="最大同时运行任务数" required>
          <a-input-number
            v-model:value="schedulerForm.max_running_tasks"
            :min="1"
            :precision="0"
            style="width: 100%"
          />
        </a-form-item>
        <a-form-item label="每日触发时刻 (HH:mm)" required>
          <a-input v-model:value="schedulerForm.daily_time" placeholder="08:00" />
        </a-form-item>
        <a-form-item label="每月触发日 (1-28)" required>
          <a-input-number
            v-model:value="schedulerForm.monthly_day"
            :min="1"
            :max="28"
            :precision="0"
            style="width: 100%"
          />
        </a-form-item>
        <a-form-item label="每月触发时刻 (HH:mm)" required>
          <a-input v-model:value="schedulerForm.monthly_time" placeholder="08:00" />
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
import { courseApi, schedulerApi, taskApi, websiteApi } from '../api'
import { useUserAccountSuggest } from '../composables/useUserAccountSuggest'

const columns = [
  { title: 'ID', dataIndex: 'id', key: 'id', width: 70, fixed: 'left' },
  { title: '网站/课程', key: 'website_course', width: 140, ellipsis: true },
  { title: '姓名/单位', key: 'user_info', width: 120, ellipsis: true },
  { title: '账号', dataIndex: 'username', key: 'username', width: 120 },
  { title: '密码', dataIndex: 'password', key: 'password', width: 120, ellipsis: true },
  { title: '模式', key: 'is_head', width: 70 },
  { title: '收费', key: 'is_charged', width: 70 },
  { title: '价格', key: 'price', width: 70 },
  { title: '进度', dataIndex: 'progress', key: 'progress', width: 90 },
  { title: '调度', key: 'schedule_type', width: 70 },
  { title: '状态', key: 'status', width: 160 },
  { title: '创建时间/完成时间', key: 'time_info', width: 170, ellipsis: true },
  { title: '备注', dataIndex: 'remark', key: 'remark', width: 140, ellipsis: true },
  { title: '操作', key: 'action', width: 300, fixed: 'right' },
]

const loading = ref(false)
const exporting = ref(false)
const submitting = ref(false)
const courseLoading = ref(false)
const dataList = ref([])
const keyword = ref('')
const statusFilter = ref(undefined)
const scheduleFilter = ref('manual')
const modalVisible = ref(false)
const editingId = ref(null)
const websiteOptions = ref([])
const courseOptions = ref([])
const startingTaskId = ref(null)
const stoppingTaskId = ref(null)
const openingBrowserId = ref(null)
const smsModalVisible = ref(false)
const smsSubmitting = ref(false)
const smsResending = ref(false)
const smsCode = ref('')
const smsTaskId = ref(null)
const schedulerRunning = ref('')
const schedulerModalVisible = ref(false)
const schedulerSaving = ref(false)
const schedulerForm = reactive({
  max_running_tasks: 5,
  daily_time: '08:00',
  monthly_day: 1,
  monthly_time: '08:00',
})

const form = reactive({
  website_id: undefined,
  course_id: undefined,
  nick_name: '',
  organ_name: '',
  username: '',
  password: '',
  is_head: '1',
  is_charged: '0',
  price: undefined,
  schedule_type: 'manual',
  remark: '',
})

const scheduleTypeLabel = (value) => {
  const map = { manual: '手动', daily: '每日', monthly: '每月' }
  return map[value || 'manual'] || value || '手动'
}

const canManualStart = (record) => {
  if (record.is_running && !record.waiting_sms) return false
  const type = record.schedule_type || 'manual'
  return type === 'manual'
}

const manualStartTip = (record) => {
  const type = record.schedule_type || 'manual'
  if (type === 'daily' || type === 'monthly') {
    return '定时任务不可手动启动，请使用「立即执行每日/每月」'
  }
  return ''
}

const {
  userSuggestOptions,
  userSuggestLoading,
  handleSelectUserAccount,
  clearUserSuggest,
  onNickNameInput,
  onWebsiteChangeForSuggest,
} = useUserAccountSuggest(form)

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

const fetchCoursesByWebsite = async (websiteId, keepCourseId = undefined, { syncPrice = true } = {}) => {
  if (!websiteId) {
    courseOptions.value = []
    form.course_id = undefined
    if (syncPrice) form.price = undefined
    return
  }
  courseLoading.value = true
  try {
    const res = await courseApi.list({ page: 1, page_size: 1000, website_id: websiteId })
    courseOptions.value = res.data.list || []
    if (keepCourseId && courseOptions.value.some((item) => item.id === keepCourseId)) {
      form.course_id = keepCourseId
    } else if (courseOptions.value.some((item) => item.id === form.course_id)) {
      // 当前课程仍属于该网站，保留
    } else {
      // 新增或切换网站：默认选中第一门课程
      form.course_id = courseOptions.value[0]?.id
    }
    if (syncPrice) {
      applyCoursePrice(form.course_id)
    }
  } finally {
    courseLoading.value = false
  }
}

const applyCoursePrice = (courseId) => {
  const course = courseOptions.value.find((item) => item.id === courseId)
  if (!course) {
    form.price = undefined
    return
  }
  form.price = course.price != null && course.price !== '' ? Number(course.price) : undefined
}

const handleCourseChange = (courseId) => {
  applyCoursePrice(courseId)
}

const handleWebsiteChange = (websiteId) => {
  fetchCoursesByWebsite(websiteId)
  onWebsiteChangeForSuggest()
}

const fetchList = async () => {
  loading.value = true
  try {
    const res = await taskApi.list({
      page: pagination.current,
      page_size: pagination.pageSize,
      keyword: keyword.value,
      status: statusFilter.value || '',
      schedule_type: scheduleFilter.value || '',
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

const parseBlobError = async (blob) => {
  try {
    const text = await blob.text()
    const data = JSON.parse(text)
    return data.message || '导出失败'
  } catch {
    return '导出失败'
  }
}

const handleExport = async () => {
  exporting.value = true
  try {
    const response = await taskApi.export({
      keyword: keyword.value,
      status: statusFilter.value || '',
      schedule_type: scheduleFilter.value || '',
    })
    const blob = response.data
    if (blob.type?.includes('application/json')) {
      message.error(await parseBlobError(blob))
      return
    }
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    const disposition = response.headers['content-disposition'] || ''
    const match = disposition.match(/filename\*?=(?:UTF-8''|")?([^";]+)/i)
    link.download = match ? decodeURIComponent(match[1].replace(/"/g, '')) : `任务列表_${Date.now()}.xlsx`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    const count = response.headers['x-total-count']
    message.success(count ? `已导出 ${count} 条任务` : '导出成功')
  } catch (error) {
    if (error.response?.data instanceof Blob) {
      message.error(await parseBlobError(error.response.data))
    } else {
      message.error(error.message || '导出失败')
    }
  } finally {
    exporting.value = false
  }
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
  form.organ_name = ''
  form.username = ''
  form.password = ''
  form.is_head = '1'
  form.is_charged = '0'
  form.price = undefined
  form.schedule_type = 'manual'
  form.remark = ''
  courseOptions.value = []
  clearUserSuggest()
}

const openModal = async (record = null) => {
  editingId.value = record?.id || null
  resetForm()
  if (record) {
    form.website_id = record.website_id || undefined
    form.nick_name = record.nick_name || ''
    form.organ_name = record.organ_name || ''
    form.username = record.username || ''
    form.password = record.password || ''
    form.is_head = record.is_head || '1'
    form.is_charged = record.is_charged || '0'
    form.price = record.price != null && record.price !== '' ? Number(record.price) : undefined
    form.schedule_type = record.schedule_type || 'manual'
    form.remark = record.remark || ''
    if (form.website_id) {
      await fetchCoursesByWebsite(form.website_id, record.course_id || undefined, { syncPrice: false })
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
      organ_name: form.organ_name.trim(),
      username: form.username,
      password: form.password,
      is_head: form.is_head,
      is_charged: form.is_charged,
      price: form.price ?? '',
      schedule_type: form.schedule_type || 'manual',
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
  } catch (error) {
    if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      message.warning('关闭请求超时，请刷新列表确认任务状态')
      fetchList()
    } else {
      message.error(error.response?.data?.message || error.message || '关闭失败')
    }
  } finally {
    stoppingTaskId.value = null
  }
}

const handleOpenBrowser = async (record) => {
  if (record.is_running) {
    message.warning('任务正在执行中，请先关闭任务')
    return
  }
  openingBrowserId.value = record.id
  const hideLoading = message.loading('正在打开页面...', 0)
  try {
    const res = await taskApi.openBrowser(record.id)
    message.success(res.message || '页面已打开')
  } finally {
    hideLoading()
    openingBrowserId.value = null
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
  if (!canManualStart(record)) {
    message.warning(manualStartTip(record) || '该任务不可手动启动')
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

const openSchedulerModal = async () => {
  try {
    const res = await schedulerApi.getConfig()
    const cfg = res.data || {}
    schedulerForm.max_running_tasks = cfg.max_running_tasks ?? 5
    schedulerForm.daily_time = cfg.daily_time || '08:00'
    schedulerForm.monthly_day = cfg.monthly_day ?? 1
    schedulerForm.monthly_time = cfg.monthly_time || '08:00'
    schedulerModalVisible.value = true
  } catch (error) {
    message.error(error.message || '读取调度配置失败')
  }
}

const handleSaveScheduler = async () => {
  schedulerSaving.value = true
  try {
    const res = await schedulerApi.updateConfig({
      max_running_tasks: schedulerForm.max_running_tasks,
      daily_time: schedulerForm.daily_time,
      monthly_day: schedulerForm.monthly_day,
      monthly_time: schedulerForm.monthly_time,
    })
    message.success(res.message || '调度配置已保存')
    schedulerModalVisible.value = false
  } finally {
    schedulerSaving.value = false
  }
}

const handleRunSchedule = async (type) => {
  schedulerRunning.value = type
  try {
    const res = await schedulerApi.run(type)
    message.success(res.message || '扫描完成')
    fetchList()
  } catch (error) {
    message.error(error.response?.data?.message || error.message || '扫描失败')
  } finally {
    schedulerRunning.value = ''
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
    smsModalVisible.value = false
    smsCode.value = ''
    smsTaskId.value = null
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

.task-table :deep(.ant-table-thead > tr > th),
.task-table :deep(.ant-table-tbody > tr > td) {
  padding-top: 6px;
  padding-bottom: 6px;
}

.stacked-cell__primary {
  line-height: 1.25;
  font-size: 13px;
}

.stacked-cell__secondary {
  color: rgba(0, 0, 0, 0.45);
  font-size: 12px;
  line-height: 1.25;
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

.user-suggest-tip {
  margin-top: 8px;
  color: rgba(0, 0, 0, 0.45);
  font-size: 12px;
}

.user-suggest {
  margin-top: 8px;
  border: 1px solid #f0f0f0;
  border-radius: 6px;
  overflow: hidden;
}

.user-suggest__tip {
  padding: 6px 10px;
  font-size: 12px;
  color: rgba(0, 0, 0, 0.45);
  background: #fafafa;
  border-bottom: 1px solid #f0f0f0;
}

.user-suggest__item {
  display: block;
  width: 100%;
  padding: 8px 10px;
  border: 0;
  border-bottom: 1px solid #f0f0f0;
  background: #fff;
  text-align: left;
  cursor: pointer;
  font-size: 13px;
  line-height: 1.4;
}

.user-suggest__item:last-child {
  border-bottom: 0;
}

.task-form :deep(.ant-form-item) {
  margin-bottom: 12px;
}

.user-suggest__item:hover {
  background: #e6f4ff;
  color: #1677ff;
}
</style>
