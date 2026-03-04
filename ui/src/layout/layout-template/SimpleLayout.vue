<script setup lang="ts">
import { computed } from 'vue'
import Sidebar from '@/layout/components/sidebar/index.vue'
import AppMain from '@/layout/app-main/index.vue'
import LayoutContainer from '@/components/layout-container/index.vue'
import UserAvatar from '@/layout/layout-header/avatar/index.vue'
import useStore from '@/stores'
import { useRoute } from 'vue-router'
const route = useRoute()
const { user } = useStore()
const {
  params: { folderId }, // id为knowledgeID
  query: { from },
} = route as any
const isShared = computed(() => {
  return (
    folderId === 'shared' ||
    from === 'systemShare' ||
    from === 'systemManage' ||
    route.path.includes('resource-management')
  )
})

// 判断是否在系统管理页面
const isSystemManagement = computed(() => {
  const path = route.path
  return path.startsWith('/system')
})

// 页面标题
const pageTitle = computed(() => {
  return 'AI-RAG'
})

// 当前系统页面
const currentSystemPage = computed(() => {
  const path = route.path
  if (path.startsWith('/system/user')) {
    return '用户管理'
  } else if (path.startsWith('/system/resource')) {
    return '资源授权'
  } else if (path.startsWith('/system/settings')) {
    return '系统设置'
  }
  return '用户管理'
})
</script>

<template>
  <div class="app-layout">
    <div class="app-main" :class="user.isExpire() ? 'isExpire' : ''" style="display: flex;">
      <!-- 最左侧侧边栏 -->
      <div style="width: 240px; border-right: 1px solid #e5e7eb;">
        <Sidebar />
      </div>
      <!-- 主内容区 -->
      <div style="flex: 1; overflow: hidden;">
        <!-- 顶部功能区（仅系统管理模式显示） -->
        <div v-if="isSystemManagement" style="display: flex; justify-content: space-between; align-items: center; padding: 16px; border-bottom: 1px solid #e5e7eb;">
          <div style="display: flex; align-items: center;">
            <h2 style="font-size: 18px; font-weight: 600; margin: 0;">AI-RAG | 系统管理</h2>
          </div>
          <div style="display: flex; align-items: center;">
            <router-link to="/application" style="display: flex; align-items: center; padding: 6px 12px; border-radius: 6px; text-decoration: none; color: #1890ff; border: 1px solid #1890ff;">
              <span style="margin-right: 4px;">←</span>
              返回工作空间
            </router-link>
          </div>
        </div>
        <AppMain />
      </div>
    </div>
  </div>
</template>
<style lang="scss">
@use './index.scss';
</style>
