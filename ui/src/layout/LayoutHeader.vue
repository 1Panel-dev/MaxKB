<script setup lang="ts">
import { useRouter } from 'vue-router'

import AvatarDropdown from './avatar-dropdown/index.vue'
import HeaderWorkspaceDropdown from './header-workspace-dropdown/index.vue'
import { isWorkspace, isSystem } from '@/router/admin/utils'
import type { LayoutMode } from './types'
const router = useRouter()
const props = withDefaults(
  defineProps<{
    mode?: LayoutMode
  }>(),
  {
    mode: 'workspace',
  },
)
function switchMode() {
  router.push(
    isWorkspace(props.mode)
      ? { name: 'system-home' }
      : { name: 'workspace-home', params: { workspaceId: 'default' } },
  )
}
</script>

<template>
  <header class="flex-between h-header px-6">
    <div class="flex items-center">
      <img src="@/assets/logo/MaxKB-logo.svg" class="h-9 max-w-none shrink-0" />
      <div class="flex items-center gap-5 ml-5">
        <el-divider direction="vertical" />
        <!-- 企业版: 工作空间下拉框 -->
        <HeaderWorkspaceDropdown v-if="isWorkspace(mode)" />
        <span v-if="isSystem(mode)" class="text-lg">系统管理</span>
      </div>
    </div>

    <div class="flex items-center gap-5">
      <el-button class="bg-primary-gradient" round>
        <MkIcon name="icon_launch_outlined" />
        <span>升级</span>
      </el-button>
      <el-divider direction="vertical" />
      <el-button v-if="isWorkspace(mode)" class="-mx-1" text @click="switchMode">
        <MkIcon name="icon_admin_outlined" />
        <span>系统管理</span>
      </el-button>
      <!--  TODO 只有系统管理员权限没有返回工作空间 -->
      <el-button v-if="isSystem(mode)" class="-mx-1" text @click="switchMode">
        <MkIcon name="icon_left_outlined" />
        <span>返回工作空间</span>
      </el-button>
      <AvatarDropdown> <!-- 头像  --> </AvatarDropdown>
    </div>
  </header>
</template>
