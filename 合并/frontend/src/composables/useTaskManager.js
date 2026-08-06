import { onMounted, reactive, ref } from 'vue'
import { message } from 'ant-design-vue'
import { courseApi, taskApi, websiteApi } from '../api'
import { useUserAccountSuggest } from './useUserAccountSuggest'

export function useTaskManager() {
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
      return false
    }
    if (!form.course_id) {
      message.warning('请选择课程')
      return false
    }
    if (!form.username.trim()) {
      message.warning('请输入账号')
      return false
    }
    if (!form.password.trim()) {
      message.warning('请输入密码')
      return false
    }
    if (form.price != null && form.price < 0) {
      message.warning('价格不能为负数')
      return false
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
      return true
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
    const hideLoading = message.loading('正在打开浏览器...', 0)
    try {
      const res = await taskApi.openBrowser(record.id)
      message.success(res.message || '浏览器已打开')
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
    const scheduleType = record.schedule_type || 'manual'
    if (scheduleType === 'daily' || scheduleType === 'monthly') {
      message.warning('定时任务不可手动启动，请在电脑端使用「立即执行每日/每月」')
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

  const loadMore = () => {
    if (loading.value) return
    if (dataList.value.length >= pagination.total) return
    pagination.current += 1
    loading.value = true
    taskApi.list({
      page: pagination.current,
      page_size: pagination.pageSize,
      keyword: keyword.value,
      status: statusFilter.value || '',
      schedule_type: scheduleFilter.value || '',
    }).then((res) => {
      dataList.value = [...dataList.value, ...res.data.list]
      pagination.total = res.data.total
    }).finally(() => {
      loading.value = false
    })
  }

  const hasMore = () => dataList.value.length < pagination.total

  const initTaskManager = () => {
    fetchWebsites()
    fetchList()
  }

  onMounted(initTaskManager)

  return {
    loading,
    exporting,
    submitting,
    courseLoading,
    dataList,
    keyword,
    statusFilter,
    scheduleFilter,
    modalVisible,
    editingId,
    websiteOptions,
    courseOptions,
    startingTaskId,
    stoppingTaskId,
    openingBrowserId,
    smsModalVisible,
    smsSubmitting,
    smsResending,
    smsCode,
    smsTaskId,
    form,
    pagination,
    userSuggestOptions,
    userSuggestLoading,
    handleSelectUserAccount,
    onNickNameInput,
    fetchWebsites,
    fetchCoursesByWebsite,
    handleWebsiteChange,
    handleCourseChange,
    fetchList,
    handleSearch,
    handleExport,
    handleTableChange,
    resetForm,
    openModal,
    handleSubmit,
    handleStop,
    handleOpenBrowser,
    handleDelete,
    handleStart,
    handleSubmitSms,
    handleResendSms,
    loadMore,
    hasMore,
    initTaskManager,
  }
}
