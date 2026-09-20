<script setup lang="ts">
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import ExecutionDetailContent from '@/workflow-canvas/execution-details/index.vue'
import { WorkflowMode } from '@/workflow-canvas/types'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'

defineOptions({ name: 'ToolWorkflowLibNodeDetail' })

withDefaults(
  defineProps<{
    data: ExecutionNodeDetail
    workflowMode?: WorkflowMode
  }>(),
  {
    workflowMode: WorkflowMode.Tool,
  },
)
</script>

<template>
  <DetailContainer :data="data">
    <template #header>
      <BaseHeader :data="data" />
    </template>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">输入参数</h6>
      <div class="whitespace-pre-wrap space-y-2">
        <p v-for="(f, i) in data.input" :key="i">
          <span class="text-N600">{{ i }}：</span>{{ f }}
        </p>
      </div>
    </div>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">输出参数</h6>
      <div class="space-y-2">
        <p v-for="(f, i) in data.output" :key="i">
          <span class="text-N600">{{ i }}：</span>{{ f }}
        </p>
      </div>
    </div>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">执行详情</h6>
      <div>
        <ExecutionDetailContent :detail="data.details" :workflow-mode="workflowMode" />
      </div>
    </div>
  </DetailContainer>
</template>
