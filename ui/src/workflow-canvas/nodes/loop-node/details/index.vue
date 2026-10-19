<script setup lang="ts">
import { computed, ref } from 'vue'
import DetailContainer from '@/workflow-canvas/execution-details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/execution-details/BaseHeader.vue'
import ExecutionDetailContent from '@/workflow-canvas/execution-details/index.vue'
import { WorkflowMode } from '@/workflow-canvas/types'
import type { ExecutionNodeDetail } from '@/workflow-canvas/execution-details/types'

defineOptions({ name: 'LoopNodeDetail' })

const props = withDefaults(
  defineProps<{
    data: ExecutionNodeDetail
    workflowMode?: WorkflowMode
  }>(),
  {
    workflowMode: WorkflowMode.Application,
  },
)

// 每一轮循环的子节点执行详情：新引擎为 children（按轮次的二维数组），兼容历史数据的 loop_node_data（以轮次下标为键的对象）。
const loopRounds = computed<ExecutionNodeDetail[][]>(() => {
  if (Array.isArray(props.data?.children)) return props.data.children
  return Object.values(props.data?.loop_node_data || {}).map((round) => Object.values(round || {}) as ExecutionNodeDetail[])
})
const loopKeys = computed(() => loopRounds.value.map((_, index) => String(index)))
const currentLoop = ref('0')

// 循环设置：新引擎放在 params 内，历史数据在顶层。
const loopType = computed(() => props.data?.params?.loop_type ?? props.data?.loop_type)
const loopSetting = computed(() => {
  const params = props.data?.params ?? props.data
  if (loopType.value === 'NUMBER') return params?.number ?? '-'
  if (loopType.value === 'ARRAY') return Array.isArray(params?.array) ? JSON.stringify(params.array) : '-'
  return loopKeys.value.length || '-'
})

// 当前选中轮次的子节点数组，交回顶层 dispatcher 递归渲染（其内部已按 index 排序、按类型分发）。
const currentLoopDetail = computed<ExecutionNodeDetail[]>(() => loopRounds.value[Number(currentLoop.value)] || [])
</script>

<template>
  <!-- 循环节点整体失败也需展示已执行轮次的子节点详情。 -->
  <DetailContainer :data="data" show-content-on-error>
    <template #header>
      <BaseHeader :data="data" />
    </template>

    <!-- 循环设置 -->
    <div class="mk-gray-card-sm">
      <h6 class="mb-2">循环设置</h6>
      <div class="space-y-2">
        <p><span class="text-N600">循环类型：</span>{{ loopType || '-' }}</p>
        <p>
          <span class="text-N600">循环数组：</span>
          {{ loopSetting }}
        </p>
      </div>
    </div>

    <!-- 循环详情 -->
    <div class="mk-gray-card-sm">
      <h6 class="mb-2">循环详情</h6>
      <div class="space-y-2">
        <template v-if="loopKeys.length > 0">
          <el-radio-group v-model="currentLoop" class="mb-2 bg-white!">
            <el-radio-button v-for="key in loopKeys" :key="key" :value="key"> {{ Number(key) + 1 }} </el-radio-button>
          </el-radio-group>
          <ExecutionDetailContent :detail="currentLoopDetail" :workflow-mode="workflowMode" />
        </template>
        <template v-else>-</template>
      </div>
    </div>
  </DetailContainer>
</template>
