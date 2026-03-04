<template>
  <div class="sidebar" style="display: flex; flex-direction: column; height: 100vh; background-color: #F9FAFB; width: 240px;">
    <!-- 顶部 Logo 区 -->
    <div style="padding: 16px;">
      <h1 style="font-size: 18px; font-weight: 600; margin: 0;">AI-RAG</h1>
    </div>
    
    <!-- 一级业务菜单 -->
    <div style="padding: 0 16px;">
      <div style="display: flex; flex-direction: column; gap: 8px;">
        <router-link to="/application" style="display: block; padding: 10px 16px; border-radius: 8px; text-decoration: none; color: #333; font-size: 14px;" :style="activeMainMenu === '/application' ? { backgroundColor: '#e6f0ff', color: '#1890ff' } : {}">
          应用
        </router-link>
        <router-link to="/knowledge" style="display: block; padding: 10px 16px; border-radius: 8px; text-decoration: none; color: #333; font-size: 14px;" :style="activeMainMenu === '/knowledge' ? { backgroundColor: '#e6f0ff', color: '#1890ff' } : {}">
          知识库
        </router-link>
        <router-link to="/tool" style="display: block; padding: 10px 16px; border-radius: 8px; text-decoration: none; color: #333; font-size: 14px;" :style="activeMainMenu === '/tool' ? { backgroundColor: '#e6f0ff', color: '#1890ff' } : {}">
          工具
        </router-link>
        <router-link to="/model" style="display: block; padding: 10px 16px; border-radius: 8px; text-decoration: none; color: #333; font-size: 14px;" :style="activeMainMenu === '/model' ? { backgroundColor: '#e6f0ff', color: '#1890ff' } : {}">
          模型
        </router-link>
      </div>
    </div>
    
    <!-- 底部用户信息区 -->
    <div style="margin-top: auto; padding: 16px; border-top: 1px solid #e5e7eb;">
      <UserAvatar />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import UserAvatar from '@/layout/layout-header/avatar/index.vue'

const route = useRoute()

const activeMainMenu = computed(() => {
  const path = route.path
  if (path.startsWith('/application')) return '/application'
  if (path.startsWith('/knowledge')) return '/knowledge'
  if (path.startsWith('/tool')) return '/tool'
  if (path.startsWith('/model')) return '/model'
  return '/application'
})

const activeSubMenu = computed(() => {
  const path = route.path
  return path
})
</script>


