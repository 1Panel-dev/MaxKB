<script setup lang="ts">
import { useRoute, useRouter } from 'vue-router'
import type { ToolItem } from '@/api/types'

defineOptions({ name: 'ToolWorkflowAction' })

const props = defineProps<{ label: string; tool: ToolItem }>()

const route = useRoute()
const router = useRouter()

function handleOpenWorkflow(event: MouseEvent) {
  event.stopPropagation()
  const workflowRoute = {
    name: 'workflow-tool',
    params: { toolId: props.tool.id, workspaceId: route.params.workspaceId },
  } as const

  if (event.ctrlKey || event.metaKey) {
    window.open(router.resolve(workflowRoute).href)
    return
  }

  router.push(workflowRoute)
}
</script>

<template>
  <MkDropdownItem @click="handleOpenWorkflow">
    <template #icon><MkIcon name="icon-setting" /></template>
    <span>{{ label }}</span>
  </MkDropdownItem>
</template>
