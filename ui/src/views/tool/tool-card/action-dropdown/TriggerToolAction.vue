<script setup lang="ts">
import type ToolApi from '@/api/admin/workspace/tool/tool'
import type SystemToolApi from '@/api/admin/system/resource-management/tool/tool'
import type ToolWorkflowApi from '@/api/admin/workspace/tool/workflow'

import { computed, nextTick, ref, useTemplateRef } from 'vue'
import type ResourceTriggerApi from '@/api/admin/workspace/trigger/resource-trigger'
import type { ResourceTriggerResource, ToolItem } from '@/api/types'
import { RESOURCE_TYPE } from '@/api/enums'
import ResourceTriggerDialog from '@/views/trigger/resource-trigger/ResourceTriggerDialog.vue'

const props = defineProps<{
  toolApi?: typeof ToolApi | typeof SystemToolApi
  toolWorkflowApi?: typeof ToolWorkflowApi
  api: typeof ResourceTriggerApi
  tool: ToolItem
  label: string
}>()
const resource = computed<ResourceTriggerResource>(() => ({
  source_type: RESOURCE_TYPE.TOOL,
  source_id: props.tool.id,
  workspace_id: props.tool.workspace_id,
}))

/* 点击后挂载资源触发器列表。 */
const dialogMounted = ref(false)
const resourceTriggerRef = useTemplateRef<InstanceType<typeof ResourceTriggerDialog>>('resourceTriggerRef')
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
  <MkAction :label="label" icon="icon-laser" @click="handleOpenTriggers" />
  <ResourceTriggerDialog
    :tool-api="toolApi"
    :tool-workflow-api="toolWorkflowApi"
    v-if="dialogMounted"
    ref="resourceTriggerRef"
    :api="api"
    :resource="resource"
    @closed="handleDialogClosed"
  />
</template>
