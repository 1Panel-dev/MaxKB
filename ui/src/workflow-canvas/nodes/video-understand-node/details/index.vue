<script setup lang="ts">
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types.ts'
import { WorkflowMode } from '@/workflow-canvas/types'
import ApplicationDetails from './application.vue'
import KnowledgeDetails from './knowledge.vue'

defineOptions({ name: 'VideoUnderstandNodeDetail' })

withDefaults(
  defineProps<{
    data: ExecutionNodeDetail
    workflowMode?: WorkflowMode
  }>(),
  {
    workflowMode: WorkflowMode.Application,
  },
)

const kv: Partial<Record<WorkflowMode, typeof ApplicationDetails>> = {
  [WorkflowMode.Application]: ApplicationDetails,
  [WorkflowMode.Knowledge]: KnowledgeDetails,
}
</script>

<template>
  <component :is="kv[workflowMode] ?? ApplicationDetails" :data="data" />
</template>
