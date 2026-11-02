<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import type WorkflowApi from '@/api/admin/workspace/knowledge/workflow'
import ExecutionRecordDrawer from './ExecutionRecordDrawer.vue'

defineOptions({ name: 'ButtonKnowledgeExecutionRecord', inheritAttrs: false })

defineProps<{ label: string; api: typeof WorkflowApi; knowledgeId: string }>()

/* 执行记录抽屉按需挂载，关闭动画结束后卸载。 */
const drawerMounted = ref(false)
const executionRecordDrawerRef = useTemplateRef<InstanceType<typeof ExecutionRecordDrawer>>('executionRecordDrawerRef')

function handleOpenExecutionRecords() {
  drawerMounted.value = true
  return nextTick(() => executionRecordDrawerRef.value?.open())
}
</script>

<template>
  <!-- 查看执行记录 -->
  <MkDropdownItem v-bind="$attrs" @click="handleOpenExecutionRecords">
    <template #icon><MkIcon name="icon_schedule-report_outlined" /></template>
    <span>{{ label }}</span>
  </MkDropdownItem>
  <ExecutionRecordDrawer v-if="drawerMounted" ref="executionRecordDrawerRef" :api="api" :knowledge-id="knowledgeId" @closed="drawerMounted = false" />
</template>
