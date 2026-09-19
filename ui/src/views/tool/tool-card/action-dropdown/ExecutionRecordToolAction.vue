<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import type ToolApi from '@/api/admin/workspace/tool/tool'
import type { ToolItem } from '@/api/types'
import ExecutionRecordDrawer from '../../execution-record/ExecutionRecordDrawer.vue'

const props = defineProps<{ api: typeof ToolApi; tool: ToolItem; label: string }>()

/* 执行记录抽屉按需挂载。 */
const drawerMounted = ref(false)
const executionRecordDrawerRef = useTemplateRef<InstanceType<typeof ExecutionRecordDrawer>>('executionRecordDrawerRef')
function handleOpenExecutionRecords() {
  drawerMounted.value = true
  return nextTick(() => executionRecordDrawerRef.value?.open())
}
function handleDrawerClosed() {
  drawerMounted.value = false
}
</script>

<template>
  <!-- 查看执行记录 -->
  <MkDropdownItem @click="handleOpenExecutionRecords">
    <template #icon><MkIcon name="icon_schedule-report_outlined" /></template>
    <span>{{ label }}</span>
  </MkDropdownItem>
  <ExecutionRecordDrawer v-if="drawerMounted" ref="executionRecordDrawerRef" :api="props.api" :tool-id="tool.id" @closed="handleDrawerClosed" />
</template>
