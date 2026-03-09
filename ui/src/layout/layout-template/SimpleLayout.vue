<template>
  <div class="app-layout" style="display: flex; flex-direction: column; height: 100vh;">
    <div class="app-header" :class="!isDefaultTheme ? 'custom-header' : ''" style="position: static;">
      <el-alert
        v-if="user.isExpire()"
        :title="$t('layout.isExpire')"
        type="warning"
        class="border-b"
        show-icon
        :closable="false"
      />
      <SystemHeader />
    </div>
    <!-- 主内容区 -->
    <div class="app-main" :class="user.isExpire() ? 'isExpire' : ''" style="display: flex; flex: 1; overflow: hidden;">
      <!-- 最左侧侧边栏 -->
      <div style="width: 240px; border-right: 1px solid #e5e7eb;">
        <Sidebar />
      </div>
      <!-- 内容区域 -->
      <div style="flex: 1; overflow: auto;">
        <AppMain />
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { computed } from 'vue'
import Sidebar from '@/layout/components/sidebar/index.vue'
import AppMain from '@/layout/app-main/index.vue'
import SystemHeader from '@/layout/layout-header/SystemHeader.vue'
import useStore from '@/stores'
import { useRoute } from 'vue-router'
const route = useRoute()
const { user, theme } = useStore()
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
const isDefaultTheme = computed(() => {
  return theme.isDefaultTheme()
})
</script>
<style lang="scss">
@use './index.scss';
</style>