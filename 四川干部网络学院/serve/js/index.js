import './toast.js'
import { request } from './request.js'
import { debounce, useBoolean } from './hooks.js'

const { ref, watch, onMounted, onUnmounted } = window.Vue
export const setup = () => {
  const thList = [
    {
      label: '序号',
      key: 'index',
      width: '3%',
    },
    {
      label: '姓名',
      key: 'nick_name',
      width: '7%',
    },
    {
      label: '单位',
      key: 'organ_name',
      width: '12%',
    },
    {
      label: '电话',
      key: 'username',
      width: '8%',
    },
    {
      label: '运行状态',
      key: 'is_running',
      width: '7%',
    },
    {
      label: '任务状态',
      key: 'status',
      width: '7%',
    },
    {
      label: '进度',
      key: 'required_period',
      width: '12%',
    },
    {
      label: '创建时间',
      key: 'create_time',
      width: '10%',
    },
    {
      label: '操作',
      key: 'opt',
      width: '34%',
    },
  ]

  const [tableLoading, toggleTableLoading] = useBoolean(false)
  const rowList = ref([])
  const total = ref(0)
  const pages = ref(0)
  const pageSizeOptions = [5, 10, 20, 50]
  const jumpPageNo = ref(1)
  const _params = {
    name: '',
    pageNo: 1,
    pageSize: 10,
  }
  const params = ref(JSON.parse(JSON.stringify(_params)))

  watch(() => params.value, (val) => {
      getData()
    },
    {
      deep: true,
    })

  const goPage = (num) => {
    params.value.pageNo = num
  }

  const jumpPage = () => {
    if (jumpPageNo.value < 1) jumpPageNo.value = 1
    if (jumpPageNo.value > pages.value) jumpPageNo.value = pages.value
    goPage(jumpPageNo.value)
  }

  const prevPage = () => {
    if (params.value.pageNo > 1) {
      params.value.pageNo--
    }
  }

  const nextPage = () => {
    if (params.value.pageNo < pages.value) {
      params.value.pageNo++
    }
  }

  const search = () => {
    if (params.value.name) {
      goPage(1)
    }
  }

  const reset = () => {
    currentId.value = ''
    params.value = JSON.parse(JSON.stringify(_params))
    getData()
  }

  const getData = debounce(() => {
    toggleTableLoading(true)
    request('GET', `/task_page`, params.value)
      .then(res => {
        if (res.code === 200) {
          rowList.value = res.data.list
          total.value = res.data.total
          pages.value = res.data.pages
        }
      })
      .catch(err => console.error('Error:', err))
      .finally(() => {
        toggleTableLoading(false)
      })
  })

  getData()

  const title = ref('')
  const [showModal, toggleModal] = useBoolean(false)
  const [modalLoading, toggleModalLoading] = useBoolean(false)
  const handleAdd = () => {
    title.value = '创建任务'
    isRetry.value = false
    step.value = 1
    autoPassword.value = false
    paramsStep1.value.password = ''
    toggleModal(true)
  }

  const step = ref(1)
  const currentId = ref(null)
  const isRetry = ref(false)
  const paramsStep1 = ref({
    username: '',
    password: '',
  })
  const autoPassword = ref(false)
  const toggleAutoPassword = () => {
    autoPassword.value = !autoPassword.value
    paramsStep1.value.password = autoPassword.value ? 'Abcd1234' : ''
  }
  const handleStep1 = () => {
    if (!paramsStep1.value.username || !paramsStep1.value.password) return
    toggleModalLoading(true)
    request('POST', `/create_task`, paramsStep1.value)
      .then(res => {
        if (res.code === 200) {
          paramsStep1.value = {
            username: '',
            password: 'Abcd1234',
          }
          currentId.value = res.data
          title.value = '提交手机验证码'
          step.value = 2
        }
        $toast(res.msg, 3000, 'top', res.code === 200 ? 'success' : 'error')
      })
      .catch(err => console.error('Error:', err))
      .finally(() => {
        toggleModalLoading(false)
      })
  }

  const paramsStep2 = ref({
    id: '',
    code: '',
  })
  const handleStep2 = () => {
    if (!paramsStep2.value.code) return
    paramsStep2.value.id = currentId.value
    toggleModalLoading(true)
    request('POST', `/submit_phone_code`, paramsStep2.value)
      .then(res => {
        if (res.code === 200) {
          paramsStep2.value = {
            id: '',
            code: '',
          }
          if (isRetry.value) {
            toggleModal(false)
            getData()
          } else {
            step.value = 3
            title.value = '课程列表'
            getCourseList()
          }
        }
        $toast(res.msg, 3000, 'top', res.code === 200 ? 'success' : 'error')
      })
      .catch(err => console.error('Error:', err))
      .finally(() => {
        toggleModalLoading(false)
      })
  }

  const courseList = ref([])
  const getCourseList = () => {
    request('GET', `/course_list`, {
      id: currentId.value,
    })
      .then(res => {
        if (res.code === 200) {
          courseList.value = res.data
        } else {
          $toast(res.msg, 3000, 'top', 'error')
        }
      })
      .catch(err => console.error('Error:', err))
  }

  const paramsStep3 = ref({
    id: '',
    class_id: '',
  })
  const selectCourse = (item) => {
    paramsStep3.value.class_id = item.id
  }
  const handleStep3 = () => {
    if (!paramsStep3.value.class_id) return
    paramsStep3.value.id = currentId.value
    toggleModalLoading(true)
    request('POST', `/submit_course`, paramsStep3.value)
      .then(res => {
        toggleModalLoading(false)
        if (res.code === 200) {
          paramsStep3.value = {
            id: '',
            class_id: '',
          }
          toggleModal(false)
          getData()
        }
        $toast(res.msg, 3000, 'top', res.code === 200 ? 'success' : 'error')
      })
      .catch(err => console.error('Error:', err))
  }

  const showCodeModal = (id) => {
    step.value = 2
    title.value = '提交手机验证码'
    paramsStep2.value.code = ''
    paramsStep2.value.id = id
    toggleModal(true)
  }

  const [retryLoading, toggleRetryLoading] = useBoolean(false)
  const handleRetry = (id) => {
    if (retryLoading.value) return
    isRetry.value = true
    currentId.value = id
    toggleRetryLoading(true)
    request('POST', `/restart_task`, {
      id,
    })
      .then(res => {
        if (res.code === 200) {
          const { status } = res.data
          if (status === '0') {
            showCodeModal(id)
          } else {
            getData()
          }
        }
        $toast(res.msg, 3000, 'top', res.code === 200 ? 'success' : 'error')
      })
      .catch(err => console.error('Error:', err))
      .finally(() => {
        toggleRetryLoading(false)
      })
  }

  const handleSendCode = (id) => {
    isRetry.value = true
    currentId.value = id
    showCodeModal(id)
  }

  const [forceRetryLoading, toggleForceRetryLoading] = useBoolean(false)
  const handleForceRetry = (id) => {
    if (forceRetryLoading.value) return
    currentId.value = id
    toggleRetryLoading(true)
    request('POST', `/force_restart_task`, {
      id,
    })
      .then(res => {
        $toast(res.msg, 3000, 'top', res.code === 200 ? 'success' : 'error')
      })
      .catch(err => console.error('Error:', err))
      .finally(() => {
        toggleForceRetryLoading(false)
      })
  }

  const [resendLoading, toggleResendLoading] = useBoolean(false)
  const resendCode = () => {
    if (resendLoading.value) return
    toggleResendLoading(true)
    request('POST', `/resend_phone_code`, {
      id: currentId.value,
    })
      .then(res => {
        $toast(res.msg, 3000, 'top', res.code === 200 ? 'success' : 'error')
      })
      .catch(err => console.error('Error:', err))
      .finally(() => {
        toggleResendLoading(false)
      })
  }

  const [openBrowserLoading, toggleOpenBrowserLoading] = useBoolean(false)
  const handleOpenBrowser = (id) => {
    if (openBrowserLoading.value) return
    currentId.value = id
    toggleOpenBrowserLoading(true)
    request('POST', `/open_browser`, {
      id,
    })
      .then(res => {
        $toast(res.msg, 3000, 'top', res.code === 200 ? 'success' : 'error')
      })
      .catch(err => console.error('Error:', err))
      .finally(() => {
        toggleOpenBrowserLoading(false)
      })
  }

  const [closeBrowserLoading, toggleCloseBrowserLoading] = useBoolean(false)
  const handleCloseBrowser = (id) => {
    if (closeBrowserLoading.value) return
    currentId.value = id
    toggleCloseBrowserLoading(true)
    request('POST', `/close_browser`, {
      id,
    })
      .then(res => {
        $toast(res.msg, 3000, 'top', res.code === 200 ? 'success' : 'error')
      })
      .catch(err => console.error('Error:', err))
      .finally(() => {
        toggleCloseBrowserLoading(false)
      })
  }

  const handleEsc = (e) => {
    if (e.key === 'Escape') {
      toggleModal(false)
    }
  }

  onMounted(() => {
    window.addEventListener('keyup', handleEsc)
  })

  onUnmounted(() => {
    window.removeEventListener('keyup', handleEsc)
  })

  return {
    thList,
    tableLoading,
    rowList,
    total,
    pages,
    pageSizeOptions,
    jumpPageNo,
    params,
    currentId,
    goPage,
    jumpPage,
    prevPage,
    nextPage,
    search,
    reset,
    title,
    showModal,
    toggleModal,
    modalLoading,
    handleAdd,
    step,
    autoPassword,
    toggleAutoPassword,
    paramsStep1,
    paramsStep2,
    paramsStep3,
    courseList,
    selectCourse,
    handleStep1,
    handleStep2,
    handleStep3,
    retryLoading,
    handleRetry,
    handleSendCode,
    forceRetryLoading,
    handleForceRetry,
    resendLoading,
    resendCode,
    openBrowserLoading,
    handleOpenBrowser,
    closeBrowserLoading,
    handleCloseBrowser,
  }
}
