<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'
import ExecutionDetailContent from '@/workflow-canvas/execution-details/index.vue'
import { WorkflowMode } from '@/workflow-canvas/types'

defineOptions({ name: 'ToolWorkflowLibNodeDetail' })

const { t } = useI18n({ useScope: 'global' })

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
  <!-- 工具工作流整体失败也需展示已执行的子节点详情。 -->
  <DetailContainer :data="data" show-content-on-error>
    <template #header>
      <BaseHeader :data="data" />
    </template>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">{{ t('workflow.executionResult.inputParams') }}</h6>
      <div class="whitespace-pre-wrap space-y-2">
        <p v-for="(f, i) in data.params ?? data.input" :key="i">
          <span class="text-N600">{{ i }}：</span>
          {{ f }}
        </p>
      </div>
    </div>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">{{ t('workflow.executionResult.outputParams') }}</h6>
      <div class="space-y-2">
        <p v-for="(f, i) in data.output" :key="i">
          <span class="text-N600">{{ i }}：</span>
          {{ f }}
        </p>
      </div>
    </div>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">{{ t('resource.executionRecords.detailTitle') }}</h6>
      <div>
        <ExecutionDetailContent :detail="data.children" :workflow-mode="workflowMode" />
      </div>
    </div>
  </DetailContainer>
</template>
