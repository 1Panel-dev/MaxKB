<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'

defineOptions({ name: 'VariableAssignNodeDetail' })
const { t } = useI18n({ useScope: 'global' })

defineProps<{
  data: ExecutionNodeDetail
}>()
</script>

<template>
  <DetailContainer :data="data">
    <template #header>
      <BaseHeader :data="data" />
    </template>

    <!-- 输入参数 -->
    <div class="mk-gray-card-sm">
      <h6 class="mb-2">{{ t('workflow.executionResult.inputParams') }}</h6>
      <div class="space-y-2">
        <p v-for="(assignment, assignmentIndex) in data.result_list" :key="assignmentIndex">
          <span class="text-N600">{{ assignment.name }} ({{ assignment.input_type }})：</span>
          {{ assignment.input_value }}
        </p>
      </div>
    </div>

    <!-- 输出参数 -->
    <div class="mk-gray-card-sm">
      <h6 class="mb-2">{{ t('workflow.executionResult.outputParams') }}</h6>
      <div class="space-y-2">
        <p v-for="(assignment, assignmentIndex) in data.result_list" :key="assignmentIndex">
          <span class="text-N600">{{ assignment.name }} ({{ assignment.output_type }})：</span>
          {{ assignment.output_value }}
        </p>
      </div>
    </div>
  </DetailContainer>
</template>
