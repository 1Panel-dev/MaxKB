<template>
  <div class="app-top-bar-container border-b flex-center">
    <div class="flex-between w-full align-center" style="padding: 0 16px;">
      <div style="display: flex; align-items: center;">
        <h1 style="font-size: 18px; font-weight: 600; margin: 0;">{{ isSystemManagement ? 'AI-RAG | 系统管理' : 'AI-RAG' }}</h1>
      </div>
      <div style="display: flex; align-items: center;">
        <router-link v-if="isSystemManagement" to="/application" style="display: flex; align-items: center; padding: 6px 12px; border-radius: 6px; text-decoration: none; color: #1890ff; border: 1px solid #1890ff;">
          <span style="margin-right: 4px;">←</span>
          返回工作空间
        </router-link>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

// 判断是否在系统管理页面
const isSystemManagement = computed(() => {
  const path = route.path
  return path.startsWith('/system') || path.startsWith('/admin/system')
})
</script>
<style lang="scss" scoped>
.app-top-bar-container {
  height: var(--app-header-height);
  box-sizing: border-box;
  padding: var(--app-header-padding);
}
</style>
