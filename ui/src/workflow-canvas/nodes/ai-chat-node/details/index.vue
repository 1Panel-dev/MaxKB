<script setup lang="ts">
import ApplicationDetails from './application.vue'
import KnowledgeDetails from './knowledge.vue'
import { WorkflowMode } from '@/workflow-canvas/types'
import type { ExecutionNodeDetail } from '@/workflow-canvas/details/types'

defineOptions({ name: 'AiChatNodeDetail' })

withDefaults(
  defineProps<{
    data: ExecutionNodeDetail
    workflowMode?: WorkflowMode
  }>(),
  {
    workflowMode: WorkflowMode.Application,
  },
)

// 按工作流模式选择详情视图；循环体等其它模式沿用应用视图。
const kv: Partial<Record<WorkflowMode, typeof ApplicationDetails>> = {
  [WorkflowMode.Application]: ApplicationDetails,
  [WorkflowMode.Knowledge]: KnowledgeDetails,
}
</script>

<template>
  <component :is="kv[workflowMode] ?? ApplicationDetails" :data="data" />
</template>
