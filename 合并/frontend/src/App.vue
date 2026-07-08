<template>
  <a-layout style="min-height: 100vh">
    <a-layout-sider v-model:collapsed="collapsed" collapsible theme="dark">
      <div class="logo">任务管理系统</div>
      <a-menu
        v-model:selectedKeys="selectedKeys"
        theme="dark"
        mode="inline"
        @click="onMenuClick"
      >
        <a-menu-item key="/websites">
          <span>网站管理</span>
        </a-menu-item>
        <a-menu-item key="/courses">
          <span>课程管理</span>
        </a-menu-item>
        <a-menu-item key="/tasks">
          <span>任务管理</span>
        </a-menu-item>
      </a-menu>
    </a-layout-sider>
    <a-layout>
      <a-layout-header class="header">
        <h2>{{ currentTitle }}</h2>
      </a-layout-header>
      <a-layout-content class="content">
        <router-view />
      </a-layout-content>
    </a-layout>
  </a-layout>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

const route = useRoute()
const router = useRouter()
const collapsed = ref(false)
const selectedKeys = ref([route.path])

const currentTitle = computed(() => route.meta.title || '任务管理系统')

watch(
  () => route.path,
  (path) => {
    selectedKeys.value = [path]
  }
)

const onMenuClick = ({ key }) => {
  router.push(key)
}
</script>

<style>
body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.logo {
  height: 64px;
  line-height: 64px;
  text-align: center;
  color: #fff;
  font-size: 16px;
  font-weight: bold;
  background: rgba(255, 255, 255, 0.1);
  margin: 0;
  overflow: hidden;
  white-space: nowrap;
}

.header {
  background: #fff;
  padding: 0 24px;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}

.header h2 {
  margin: 0;
  line-height: 64px;
  font-size: 18px;
}

.content {
  margin: 24px;
  padding: 24px;
  background: #fff;
  border-radius: 8px;
  min-height: 360px;
}
</style>
