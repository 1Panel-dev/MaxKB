<script setup lang="ts">
import DetailContainer from '@/workflow-canvas/details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/details/BaseHeader.vue'
import type { ExecutionNodeDetail } from '@/workflow-canvas/details/types'

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
    <template #header="{ show }">
      <BaseHeader :data="data" :show="show" />
    </template>

    <div class="overflow-hidden rounded-md bg-N100">
      <h5 class="px-3 py-2">聚合策略</h5>
      <div class="whitespace-pre-wrap border-t border-dashed px-3 py-2 text-N900">
        {{ strategyLabel(data.strategy) }}
      </div>
    </div>

    <div
      v-for="(group, groupI) in data.group_list"
      :key="groupI"
      class="overflow-hidden rounded-md bg-N100"
    >
      <h5 class="px-3 py-2">{{ group.label }}输入参数</h5>
      <el-scrollbar height="200">
        <div class="border-t border-dashed px-3 py-2 text-N900">
          <p v-for="(f, i) in group.variable_list" :key="i" class="mb-2">
            <span class="mr-1 text-N600">{{ `${f.node_name}.${f.field}` }}:</span>{{ f.value }}
          </p>
        </div>
      </el-scrollbar>
    </div>

    <div class="overflow-hidden rounded-md bg-N100">
      <h5 class="px-3 py-2">输出参数</h5>
      <el-scrollbar height="200">
        <div class="border-t border-dashed px-3 py-2 text-N900">
          <p v-for="(f, i) in data.result" :key="i" class="mb-2">
            <span class="mr-1 text-N600">{{ i }}:</span>{{ f }}
          </p>
        </div>
      </el-scrollbar>
    </div>
  </DetailContainer>
</template>
