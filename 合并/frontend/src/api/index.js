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
    message.error(error.message || '网络错误')
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
  start: (id) => request.post(`/tasks/${id}/start`),
}

export default request
