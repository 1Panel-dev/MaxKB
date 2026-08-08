<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import MkWorkspaceDropdown from '@/components/mk-workspace-dropdown/index.vue'
import { useStore } from '@/stores'
import type { WorkspaceItem } from '@/types'

defineOptions({ name: 'WorkspaceDropdown' })
const router = useRouter()
const route = useRoute()
const { user } = useStore()

const workspaceOptions = computed<WorkspaceItem[]>(() => {
  const workspaces = user.userInfo?.workspace_list
  return workspaces?.length ? workspaces : [{ id: 'default', name: '默认工作空间' }]
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
  void router.push({
    name: route.name,
    params: { ...route.params, workspaceId },
    query: route.query,
    hash: route.hash,
  })
}
</script>

<template>
  <MkWorkspaceDropdown
    v-model="selectedWorkspace"
    :options="workspaceOptions"
    @select="handleWorkspaceSelect"
  />
</template>
