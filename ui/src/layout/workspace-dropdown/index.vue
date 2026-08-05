<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import MkWorkspaceDropdown from '@/components/mk-workspace-dropdown/index.vue'
import { useStore } from '@/stores'
import type { DropdownOption } from '@/types'

defineOptions({ name: 'WorkspaceDropdown' })
const router = useRouter()
const route = useRoute()
const { user } = useStore()

const workspaceOptions = computed<DropdownOption[]>(() => {
  const workspaces = user.userInfo?.workspace_list
  return workspaces?.length
    ? workspaces.map(({ id, name }) => ({ value: id ?? 'default', label: name }))
    : [{ value: 'default', label: '默认工作空间' }]
})
const selectedWorkspace = ref<string | number>('default')

watch(
  () => route.params.workspaceId,
  (val) => {
    selectedWorkspace.value = String(val ?? 'default')
  },
  { immediate: true },
)

function handleWorkspaceSelect(option: DropdownOption) {
  const workspaceId = String(option.value)
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
