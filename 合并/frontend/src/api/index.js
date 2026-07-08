import axios from 'axios'
import { message } from 'ant-design-vue'

const request = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

request.interceptors.response.use(
  (response) => {
    const res = response.data
    if (res.code !== 200) {
      message.error(res.message || '请求失败')
      return Promise.reject(new Error(res.message || '请求失败'))
    }
    return res
  },
  (error) => {
    if (error.config?.skipGlobalError) {
      return Promise.reject(error)
    }
    if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
      message.error('请求超时，请稍后刷新列表查看任务状态')
    } else {
      message.error(error.response?.data?.message || error.message || '网络错误')
    }
    return Promise.reject(error)
  }
)

export const websiteApi = {
  list: (params) => request.get('/websites', { params }),
  create: (data) => request.post('/websites', data),
  update: (id, data) => request.put(`/websites/${id}`, data),
  delete: (id) => request.delete(`/websites/${id}`),
}

export const courseApi = {
  list: (params) => request.get('/courses', { params }),
  create: (data) => request.post('/courses', data),
  update: (id, data) => request.put(`/courses/${id}`, data),
  delete: (id) => request.delete(`/courses/${id}`),
}

export const taskApi = {
  list: (params) => request.get('/tasks', { params }),
  create: (data) => request.post('/tasks', data),
  update: (id, data) => request.put(`/tasks/${id}`, data),
  delete: (id) => request.delete(`/tasks/${id}`),
  // 启动含浏览器登录，耗时较长
  start: (id) => request.post(`/tasks/${id}/start`, null, { timeout: 120000, skipGlobalError: true }),
  submitSmsCode: (id, code) => request.post(`/tasks/${id}/sms-code`, { code }, { timeout: 60000 }),
  resendSmsCode: (id) => request.post(`/tasks/${id}/resend-sms`, null, { timeout: 30000 }),
  stop: (id) => request.post(`/tasks/${id}/stop`, null, { timeout: 30000 }),
}

export default request
