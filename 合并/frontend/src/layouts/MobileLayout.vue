<template>
  <div class="mobile-layout">
    <header class="mobile-header">
      <h1 class="mobile-header__title">{{ title }}</h1>
    </header>
    <main class="mobile-main">
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const title = computed(() => route.meta.title || '任务管理')
</script>

<style scoped>
.mobile-layout {
  min-height: 100vh;
  min-height: 100dvh;
  background: #f5f6f8;
  display: flex;
  flex-direction: column;
}

.mobile-header {
  position: sticky;
  top: 0;
  z-index: 100;
  background: linear-gradient(135deg, #1677ff 0%, #0958d9 100%);
  padding: calc(12px + env(safe-area-inset-top, 0)) 16px 12px;
  box-shadow: 0 2px 8px rgba(22, 119, 255, 0.25);
}

.mobile-header__title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #fff;
  text-align: center;
}

.mobile-main {
  flex: 1;
  overflow: auto;
  -webkit-overflow-scrolling: touch;
}
</style>
