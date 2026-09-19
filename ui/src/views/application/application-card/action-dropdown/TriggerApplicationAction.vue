<script setup lang="ts">
import { computed, nextTick, ref, useTemplateRef } from 'vue'
import type ResourceTriggerApi from '@/api/admin/workspace/trigger/resource-trigger'
import type { ApplicationDetail, ResourceTriggerResource } from '@/api/types'
import { RESOURCE_TYPE } from '@/api/enums'
import { MsgError } from '@/utils/message'
import ResourceTriggerDialog from '@/views/trigger/resource-trigger/ResourceTriggerDialog.vue'

const props = defineProps<{ api: typeof ResourceTriggerApi; application: ApplicationDetail; label: string }>()
const resource = computed<ResourceTriggerResource | undefined>(() => {
  const workspaceId = props.application.workspace_id
  if (!workspaceId) return
  return {
    source_type: RESOURCE_TYPE.APPLICATION,
    source_id: props.application.id,
    workspace_id: workspaceId,
  }
})

/* 点击后挂载资源触发器列表。 */
const dialogMounted = ref(false)
const resourceTriggerRef = useTemplateRef<InstanceType<typeof ResourceTriggerDialog>>('resourceTriggerRef')
function handleOpenTriggers() {
  if (!resource.value) {
    MsgError('智能体缺少所属工作空间信息')
    return
  }
  dialogMounted.value = true
  return nextTick(() => resourceTriggerRef.value?.open())
}
function handleDialogClosed() {
  dialogMounted.value = false
}
</script>

<template>
  <!-- 查看智能体触发器 -->
  <MkDropdownItem @click="handleOpenTriggers" :disabled="!application.is_publish">
    <template #icon><MkIcon name="icon-laser" /></template>
    <span>{{ label }}</span>
  </MkDropdownItem>
  <ResourceTriggerDialog v-if="dialogMounted && resource" ref="resourceTriggerRef" :api="api" :resource="resource" @closed="handleDialogClosed" />
</template>
