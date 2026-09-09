<script setup lang="ts">
import ApplicationDetails from './application.vue'
import KnowledgeDetails from './knowledge.vue'
import { WorkflowMode } from '@/workflow-canvas/types'
import type { ExecutionNodeDetail } from '@/workflow-canvas/details/types'

defineOptions({ name: 'ImageUnderstandNodeDetail' })

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
