<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import type ResourceTriggerApi from '@/api/admin/workspace/trigger/resource-trigger'
import type ApplicationApi from '@/api/admin/workspace/application/application'
import type SystemResourceApplicationApi from '@/api/admin/system/resource-management/application/application'
import type { ApplicationDetail } from '@/api/types'
import { MsgError } from '@/utils/message'
import ApplicationTriggerDialog from './ApplicationTriggerDialog.vue'

const props = defineProps<{
  api: typeof ResourceTriggerApi
  applicationApi?: typeof ApplicationApi | typeof SystemResourceApplicationApi
  application: ApplicationDetail
  label: string
}>()

/* 点击后挂载资源触发器列表。 */
const dialogMounted = ref(false)
const resourceTriggerRef = useTemplateRef<InstanceType<typeof ApplicationTriggerDialog>>('resourceTriggerRef')
function handleOpenTriggers() {
  if (!props.application.workspace_id) {
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
  <ApplicationTriggerDialog
    v-if="dialogMounted"
    ref="resourceTriggerRef"
    :api="api"
    :application-api="applicationApi"
    :application="application"
    @closed="handleDialogClosed"
  />
</template>
