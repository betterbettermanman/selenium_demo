import { createRouter, createWebHistory } from 'vue-router'
import WebsiteList from '../views/WebsiteList.vue'
import CourseList from '../views/CourseList.vue'
import TaskList from '../views/TaskList.vue'

const routes = [
  { path: '/', redirect: '/websites' },
  { path: '/websites', name: 'WebsiteList', component: WebsiteList, meta: { title: '网站管理' } },
  { path: '/courses', name: 'CourseList', component: CourseList, meta: { title: '课程管理' } },
  { path: '/tasks', name: 'TaskList', component: TaskList, meta: { title: '任务管理' } },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
