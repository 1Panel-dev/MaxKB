<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import type { WorkspaceItem } from '@/api/types'
import WorkspaceDropdown from '@/components/business/workspace-dropdown/index.vue'
import { useStore } from '@/stores'
import { getRoleName } from '@/utils/role-name'

defineOptions({ name: 'HeaderWorkspaceDropdown' })
const { t } = useI18n({ useScope: 'global' })

const router = useRouter()
const route = useRoute()
const { user } = useStore()

const workspaceOptions = computed<WorkspaceItem[]>(() => {
  const workspaces = user.userInfo?.workspace_list
  if (!workspaces?.length) return [{ id: 'default', name: t('workspace.default') }]
  return workspaces.map((workspace) => ({
    ...workspace,
    role_name: workspace.role_info?.map(({ role_id, role_name }) => getRoleName(role_id, role_name)) ?? workspace.role_name,
  }))
})
const selectedWorkspace = ref('default')

watch(
  () => route.params.workspaceId,
  (val) => {
    selectedWorkspace.value = String(val ?? 'default')
  },
  { immediate: true },
)

function handleWorkspaceSelect(workspace: WorkspaceItem) {
  const workspaceId = workspace.id ?? 'default'
  if (workspaceId === route.params.workspaceId || !route.name) return
  // 详情中的资源属于原工作空间，切换后回到对应列表。
  let listRouteName: string | undefined
  if (route.meta.resourceDetailRoot) {
    if (route.params.applicationId) listRouteName = 'workspace-application-list'
    else if (route.params.knowledgeId) listRouteName = 'workspace-knowledge-list'
  }
  const targetRoute = router.resolve(
    listRouteName
      ? { name: listRouteName, params: { workspaceId } }
      : { name: route.name, params: { ...route.params, workspaceId }, query: route.query, hash: route.hash },
  )
  // 切换工作空间时整页加载，重新初始化用户权限和页面状态。
  window.location.assign(targetRoute.href)
}
</script>

<template>
  <WorkspaceDropdown v-model="selectedWorkspace" :options="workspaceOptions" @select="handleWorkspaceSelect" showRoleTags />
</template>
