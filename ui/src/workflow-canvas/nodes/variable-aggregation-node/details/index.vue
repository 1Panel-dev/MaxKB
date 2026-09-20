<script setup lang="ts">
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'

defineOptions({ name: 'VariableAggregationNodeDetail' })

defineProps<{
  data: ExecutionNodeDetail
}>()

const strategyLabel = (strategy?: string) => {
  if (strategy === 'first_non_null') return '返回每组变量的第一个非空值'
  if (strategy === 'variable_to_dict') return '返回每组变量的字典（Dict）'
  return '返回每组变量的数组（Array）'
}
</script>

<template>
  <DetailContainer :data="data">
    <template #header>
      <BaseHeader :data="data" />
    </template>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">聚合策略</h6>
      <div class="whitespace-pre-wrap">
        {{ strategyLabel(data.strategy) }}
      </div>
    </div>

    <div v-for="(group, groupI) in data.group_list" :key="groupI" class="mk-gray-card-sm">
      <h6 class="mb-2">{{ group.label }}输入参数</h6>
      <el-scrollbar max-height="200">
        <div class="space-y-2">
          <p v-for="(f, i) in group.variable_list" :key="i">
            <span class="text-N600">{{ `${f.node_name}.${f.field}` }}：</span>{{ f.value }}
          </p>
        </div>
      </el-scrollbar>
    </div>

    <div class="mk-gray-card-sm">
      <h6 class="mb-2">输出参数</h6>
      <el-scrollbar max-height="200">
        <div class="space-y-2">
          <p v-for="(f, i) in data.result" :key="i">
            <span class="text-N600">{{ i }}：</span>{{ f }}
          </p>
        </div>
      </el-scrollbar>
    </div>
  </DetailContainer>
</template>
