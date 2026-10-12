<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import type WorkflowApi from '@/api/admin/workspace/knowledge/workflow'
import ExecutionRecordDrawer from '@/views/workflow/knowledge/execution-record/ExecutionRecordDrawer.vue'

defineOptions({ name: 'ButtonExecutionRecord' })
defineProps<{ api: typeof WorkflowApi; knowledgeId: string }>()

/* 执行记录抽屉按需挂载，关闭动画结束后卸载。 */
const drawerMounted = ref(false)
const executionRecordDrawerRef = useTemplateRef<InstanceType<typeof ExecutionRecordDrawer>>('executionRecordDrawerRef')

function handleOpenExecutionRecords() {
  if (drawerMounted.value) return
  drawerMounted.value = true
  return nextTick(() => executionRecordDrawerRef.value?.open())
}
</script>

<template>
  <span>
    <!-- 查看工作流执行记录 -->
    <el-button plain @click="handleOpenExecutionRecords">
      <MkIcon name="icon_schedule-report_outlined" />
      <span>执行记录</span>
    </el-button>
  </span>
  <ExecutionRecordDrawer v-if="drawerMounted" ref="executionRecordDrawerRef" :api="api" :knowledge-id="knowledgeId" @closed="drawerMounted = false" />
</template>
