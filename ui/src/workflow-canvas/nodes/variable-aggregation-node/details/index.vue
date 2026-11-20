<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'

defineOptions({ name: 'VariableAggregationNodeDetail' })
const { t } = useI18n({ useScope: 'global' })

defineProps<{
  data: ExecutionNodeDetail
}>()

const strategyLabel = (strategy?: string) => {
  if (strategy === 'first_non_null') return t('workflow.variableAggregation.strategy.firstNonNullDescription')
  if (strategy === 'variable_to_dict') return t('workflow.variableAggregation.strategy.dict')
  return t('workflow.variableAggregation.strategy.array')
}
</script>

<template>
  <DetailContainer :data="data">
    <template #header>
      <BaseHeader :data="data" />
    </template>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">{{ t('workflow.variableAggregation.strategy.label') }}</h6>
      <div class="whitespace-pre-wrap">
        {{ strategyLabel(data.strategy) }}
      </div>
    </div>

    <div v-for="(group, groupI) in data.group_list" :key="groupI" class="mk-gray-card-sm">
      <h6 class="mb-2">{{ group.label }} {{ t('execution.details.inputParams') }}</h6>
      <div class="space-y-2">
        <p v-for="(f, i) in group.variable_list" :key="i">
          <span class="text-N600">{{ `${f.node_name}.${f.field}` }}：</span>
          {{ f.value }}
        </p>
      </div>
    </div>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">{{ t('execution.details.outputParams') }}</h6>
      <div class="space-y-2">
        <p v-for="(f, i) in data.result" :key="i">
          <span class="text-N600">{{ i }}：</span>
          {{ f }}
        </p>
      </div>
    </div>
  </DetailContainer>
</template>
