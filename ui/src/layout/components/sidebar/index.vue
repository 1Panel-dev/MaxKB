<template>
  <div class="sidebar" style="display: flex; flex-direction: column; height: 100%; background-color: #F9FAFB; width: 240px;">
    <!-- 顶部 Logo 区 -->
    <div style="padding: 16px;">
    </div>

    <!-- 业务菜单或系统管理菜单 -->
    <div style="padding: 0 16px;">
      <!-- 业务菜单 -->
      <div v-if="!isSystemManagement" style="display: flex; flex-direction: column; gap: 8px;">
        <router-link to="/application" style="display: block; padding: 10px 16px; border-radius: 8px; text-decoration: none; color: #333; font-size: 14px;" :style="activeMainMenu === '/application' ? { backgroundColor: '#e6f0ff', color: '#1890ff' } : {}">
          应用
        </router-link>
        <router-link to="/mindmap" style="display: block; padding: 10px 16px; border-radius: 8px; text-decoration: none; color: #333; font-size: 14px;" :style="activeMainMenu === '/mindmap' ? { backgroundColor: '#e6f0ff', color: '#1890ff' } : {}">
          思维导图
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

      <!-- 系统管理菜单 -->
      <div v-else style="display: flex; flex-direction: column; gap: 8px;">
        <router-link to="/system/user" style="display: block; padding: 10px 16px; border-radius: 8px; text-decoration: none; color: #333; font-size: 14px;" :style="activeSystemMenu === '/system/user' ? { backgroundColor: '#e6f0ff', color: '#1890ff' } : {}">
          用户管理
        </router-link>

        <!-- 资源授权（下拉展开） -->
        <div>
          <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 16px; border-radius: 8px; cursor: pointer;" :style="activeSystemMenu.startsWith('/system/authorization') ? { backgroundColor: '#e6f0ff', color: '#1890ff' } : {}" @click="toggleResourceAuth">
            <span>资源授权</span>
            <span>{{ resourceAuthExpanded ? '▼' : '▶' }}</span>
          </div>
          <div v-if="resourceAuthExpanded" style="padding-left: 32px; margin-top: 4px; display: flex; flex-direction: column; gap: 4px;">
            <router-link to="/system/authorization/application" style="display: block; padding: 8px 16px; border-radius: 8px; text-decoration: none; color: #666; font-size: 13px;" :style="activeSystemMenu === '/system/authorization/application' ? { backgroundColor: '#e6f0ff', color: '#1890ff' } : {}">
              应用
            </router-link>
            <router-link to="/system/authorization/knowledge" style="display: block; padding: 8px 16px; border-radius: 8px; text-decoration: none; color: #666; font-size: 13px;" :style="activeSystemMenu === '/system/authorization/knowledge' ? { backgroundColor: '#e6f0ff', color: '#1890ff' } : {}">
              知识库
            </router-link>
            <router-link to="/system/authorization/tool" style="display: block; padding: 8px 16px; border-radius: 8px; text-decoration: none; color: #666; font-size: 13px;" :style="activeSystemMenu === '/system/authorization/tool' ? { backgroundColor: '#e6f0ff', color: '#1890ff' } : {}">
              工具
            </router-link>
            <router-link to="/system/authorization/model" style="display: block; padding: 8px 16px; border-radius: 8px; text-decoration: none; color: #666; font-size: 13px;" :style="activeSystemMenu === '/system/authorization/model' ? { backgroundColor: '#e6f0ff', color: '#1890ff' } : {}">
              模型
            </router-link>
          </div>
        </div>

        <!-- 系统设置（下拉展开） -->
        <div>
          <div style="display: flex; justify-content: space-between; align-items: center; padding: 10px 16px; border-radius: 8px; cursor: pointer;" :style="activeSystemMenu.startsWith('/system/email') ? { backgroundColor: '#e6f0ff', color: '#1890ff' } : {}" @click="toggleSystemSettings">
            <span>系统设置</span>
            <span>{{ systemSettingsExpanded ? '▼' : '▶' }}</span>
          </div>
          <div v-if="systemSettingsExpanded" style="padding-left: 32px; margin-top: 4px; display: flex; flex-direction: column; gap: 4px;">
            <router-link to="/system/email" style="display: block; padding: 8px 16px; border-radius: 8px; text-decoration: none; color: #666; font-size: 13px;" :style="activeSystemMenu === '/system/email' ? { backgroundColor: '#e6f0ff', color: '#1890ff' } : {}">
              邮件设置
            </router-link>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部用户信息区 -->
    <div style="margin-top: auto; padding: 16px; border-top: 1px solid #e5e7eb;">
      <UserAvatar />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import UserAvatar from '@/layout/layout-header/avatar/index.vue'

const route = useRoute()

// 判断是否在系统管理页面
const isSystemManagement = computed(() => {
  const path = route.path
  return path.startsWith('/system')
})

// 业务菜单激活状态
const activeMainMenu = computed(() => {
  const path = route.path
  if (path.startsWith('/application')) return '/application'
  if (path.startsWith('/mindmap')) return '/mindmap'
  if (path.startsWith('/knowledge')) return '/knowledge'
  if (path.startsWith('/tool')) return '/tool'
  if (path.startsWith('/model')) return '/model'
  return '/application'
})

// 系统管理菜单激活状态
const activeSystemMenu = computed(() => {
  const path = route.path
  if (path.startsWith('/system/user')) return '/system/user'
  if (path.startsWith('/system/authorization')) return path
  if (path.startsWith('/system/email')) return path
  return '/system/user'
})

// 资源授权下拉菜单展开状态
const resourceAuthExpanded = ref(false)
// 系统设置下拉菜单展开状态
const systemSettingsExpanded = ref(false)

// 切换资源授权下拉菜单
const toggleResourceAuth = () => {
  resourceAuthExpanded.value = !resourceAuthExpanded.value
  // 关闭其他下拉菜单
  systemSettingsExpanded.value = false
}

// 切换系统设置下拉菜单
const toggleSystemSettings = () => {
  systemSettingsExpanded.value = !systemSettingsExpanded.value
  // 关闭其他下拉菜单
  resourceAuthExpanded.value = false
}

const activeSubMenu = computed(() => {
  const path = route.path
  return path
})

// 确保组件挂载时下拉菜单保持折叠状态
onMounted(() => {
  resourceAuthExpanded.value = false
  systemSettingsExpanded.value = false
})
</script>


