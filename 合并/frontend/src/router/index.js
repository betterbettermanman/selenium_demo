import { createRouter, createWebHistory } from 'vue-router'
import PcLayout from '../layouts/PcLayout.vue'
import MobileLayout from '../layouts/MobileLayout.vue'
import WebsiteList from '../views/WebsiteList.vue'
import CourseList from '../views/CourseList.vue'
import TaskList from '../views/TaskList.vue'
import UserAccountList from '../views/UserAccountList.vue'
import MobileTaskList from '../views/mobile/MobileTaskList.vue'

const routes = [
  {
    path: '/',
    component: PcLayout,
    children: [
      { path: '', redirect: '/websites' },
      { path: 'websites', name: 'WebsiteList', component: WebsiteList, meta: { title: '网站管理' } },
      { path: 'courses', name: 'CourseList', component: CourseList, meta: { title: '课程管理' } },
      { path: 'tasks', name: 'TaskList', component: TaskList, meta: { title: '任务管理' } },
      { path: 'user-accounts', name: 'UserAccountList', component: UserAccountList, meta: { title: '用户管理' } },
    ],
  },
  {
    path: '/m',
    component: MobileLayout,
    meta: { mobile: true },
    children: [
      { path: '', redirect: '/m/tasks' },
      { path: 'tasks', name: 'MobileTaskList', component: MobileTaskList, meta: { title: '任务管理', mobile: true } },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

export default router
