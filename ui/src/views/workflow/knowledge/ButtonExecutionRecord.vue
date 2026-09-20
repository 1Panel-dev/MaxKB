<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import WorkflowApi from '@/api/admin/workspace/knowledge/workflow'
import ExecutionRecordDrawer from './execution-record/ExecutionRecordDrawer.vue'

defineOptions({ name: 'ButtonKnowledgeExecutionRecord', inheritAttrs: false })

defineProps<{ knowledgeId: string }>()

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
    <span>执行记录</span>
  </MkDropdownItem>
  <ExecutionRecordDrawer
    v-if="drawerMounted"
    ref="executionRecordDrawerRef"
    :api="WorkflowApi"
    :knowledge-id="knowledgeId"
    @closed="drawerMounted = false"
  />
</template>
