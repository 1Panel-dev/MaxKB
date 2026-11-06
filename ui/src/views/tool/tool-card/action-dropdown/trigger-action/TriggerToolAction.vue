<script setup lang="ts">
import type ToolApi from '@/api/admin/workspace/tool/tool'
import type SystemToolApi from '@/api/admin/system/resource-management/tool/tool'
import type ToolWorkflowApi from '@/api/admin/workspace/tool/workflow'

import { nextTick, ref, useTemplateRef } from 'vue'
import type ResourceTriggerApi from '@/api/admin/workspace/trigger/resource-trigger'
import type { ToolItem } from '@/api/types'
import ToolTriggerDialog from './ToolTriggerDialog.vue'

defineProps<{
  toolApi?: typeof ToolApi | typeof SystemToolApi
  toolWorkflowApi?: typeof ToolWorkflowApi
  api: typeof ResourceTriggerApi
  tool: ToolItem
  label: string
}>()

/* 点击后挂载资源触发器列表。 */
const dialogMounted = ref(false)
const resourceTriggerRef = useTemplateRef<InstanceType<typeof ToolTriggerDialog>>('resourceTriggerRef')
function handleOpenTriggers() {
  dialogMounted.value = true
  return nextTick(() => resourceTriggerRef.value?.open())
}
function handleDialogClosed() {
  dialogMounted.value = false
}
</script>

<template>
  <!-- 查看工具触发器 -->
  <MkDropdownItem @click="handleOpenTriggers">
    <template #icon><MkIcon name="icon-laser" /></template>
    <span>{{ label }}</span>
  </MkDropdownItem>
  <ToolTriggerDialog
    :tool-api="toolApi"
    :tool-workflow-api="toolWorkflowApi"
    v-if="dialogMounted"
    ref="resourceTriggerRef"
    :api="api"
    :tool="tool"
    @closed="handleDialogClosed"
  />
</template>
