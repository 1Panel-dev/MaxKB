<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'

import AvatarDropdown from './avatar-dropdown/index.vue'
import HeaderWorkspaceDropdown from './header-workspace-dropdown/index.vue'
import { isSystem, isWorkspace } from './utils'
import LogoFull from '@/components/mk-logo/LogoFull.vue'
import type { LayoutMode } from './types'
import { Compare, hasPermission, Role, RoleConstants } from '@/permission/core'
import { getWorkspaceId } from '@/utils/resource-context'
import { useStore } from '@/stores'

const router = useRouter()
const props = withDefaults(defineProps<{ mode?: LayoutMode; preview?: boolean }>(), { mode: 'workspace', preview: false })

const { user } = useStore()

// 命中 "X" / "X:..." / "X:w:..."（系统模式下没有 workspaceId，仍能匹配 EXTENDS_*）
function hasRolePrefix(name: string) {
  for (const role of user.roleSet) {
    if (role === name || role.startsWith(`${name}:`)) return true
  }
  return false
}

// 系统管理员：内置 ADMIN 或自定义 ADMIN 类型（EXTENDS_ADMIN 无 :w: 后缀）
const canManageSystem = computed(() =>
  hasPermission([RoleConstants.ADMIN, RoleConstants.EXTENDS_ADMIN], Compare.OR),
)

// 工作空间管理员：内置 WORKSPACE_MANAGE 或自定义 EXTENDS_WORKSPACE_MANAGE
const isWorkspaceManager = computed(() => {
  const workspaceId = getWorkspaceId()
  return (
    hasPermission(
      [RoleConstants.WORKSPACE_MANAGE, new Role(RoleConstants.WORKSPACE_MANAGE.name, workspaceId)],
      Compare.OR,
    ) || hasRolePrefix(RoleConstants.EXTENDS_WORKSPACE_MANAGE.name)
  )
})

// 普通用户：内置 USER 或自定义 EXTENDS_USER
const isOrdinaryUser = computed(() => {
  const workspaceId = getWorkspaceId()
  return (
    hasPermission([RoleConstants.USER, new Role(RoleConstants.USER.name, workspaceId)], Compare.OR) ||
    hasRolePrefix(RoleConstants.EXTENDS_USER.name)
  )
})

// 「返回工作空间」：工作空间管理员或普通用户
const canReturnWorkspace = computed(() => isWorkspaceManager.value || isOrdinaryUser.value)

function switchMode() {
  if (isWorkspace(props.mode)) {
    router.push({ name: 'system-home' })
    return
  }
  const workspaceId = user.userInfo?.workspace_list?.[0]?.id || 'default'
  router.push({ name: 'workspace-home', params: { workspaceId } })
}
</script>

<template>
  <header class="flex-between h-header px-6">
    <div class="flex-align-center">
      <LogoFull class="shrink-0" />
      <div v-if="!preview" class="flex-align-center gap-5 ml-5">
        <el-divider direction="vertical" />
        <!-- 企业版: 工作空间下拉框 -->
        <HeaderWorkspaceDropdown v-if="isWorkspace(mode)" />
        <span v-if="isSystem(mode)">系统管理</span>
      </div>
    </div>

    <div class="flex-align-center gap-5">
      <el-button v-if="!preview" class="bg-primary-gradient" round>
        <MkIcon name="icon_launch_outlined" />
        <span>升级</span>
      </el-button>
      <el-divider direction="vertical" />
      <el-button v-if="isWorkspace(mode) && (isWorkspaceManager || canManageSystem )" class="-mx-1" text @click="switchMode">
        <MkIcon name="icon_admin_outlined" />
        <span>系统管理</span>
      </el-button>
      <!--  TODO 只有系统管理员权限没有返回工作空间 -->
      <el-button v-if="isSystem(mode) && canReturnWorkspace" class="-mx-1" text @click="switchMode">
        <MkIcon name="icon_left_outlined" />
        <span>返回工作空间</span>
      </el-button>
      <AvatarDropdown> <!-- 头像  --> </AvatarDropdown>
    </div>
  </header>
</template>
