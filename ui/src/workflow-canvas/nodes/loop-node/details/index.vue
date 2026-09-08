<script setup lang="ts">
import { computed, ref } from 'vue'
import DetailContainer from '@/workflow-canvas/details/DetailContainer.vue'
import BaseHeader from '@/workflow-canvas/details/BaseHeader.vue'
import ExecutionDetailContent from '@/workflow-canvas/details/index.vue'
import { WorkflowMode } from '@/workflow-canvas/types'
import type { ExecutionNodeDetail } from '@/workflow-canvas/details/types'

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

// 每一轮循环的子节点执行详情，键为轮次下标。
const loopKeys = computed(() => Object.keys(props.data?.loop_node_data || {}))
const currentLoop = ref(loopKeys.value[0] ?? '')

// 当前选中轮次的子节点数组，交回顶层 dispatcher 递归渲染（其内部已按 index 排序、按类型分发）。
const currentLoopDetail = computed<ExecutionNodeDetail[]>(() =>
  Object.values(props.data?.loop_node_data?.[currentLoop.value] || {}),
)
</script>

<template>
  <!-- 循环节点整体失败也需展示已执行轮次的子节点详情。 -->
  <DetailContainer :data="data" show-content-on-error>
    <template #header="{ show }">
      <BaseHeader :data="data" :show="show" />
    </template>

    <!-- 循环设置 -->
    <div class="overflow-hidden rounded-md bg-N100">
      <h5 class="px-3 py-2">循环设置</h5>
      <div class="border-t border-dashed px-3 py-2 text-N900">
        <p class="mb-2"><span class="mr-1 text-N600">循环类型:</span>{{ data.loop_type || '-' }}</p>
        <p>
          <span class="mr-1 text-N600">循环数组:</span>
          {{ data.loop_type === 'NUMBER' ? data.number : loopKeys.join(', ') || '-' }}
        </p>
      </div>
    </div>

    <!-- 循环详情 -->
    <div class="overflow-hidden rounded-md bg-N100">
      <h5 class="px-3 py-2">循环详情</h5>
      <div class="border-t border-dashed px-3 py-2 text-N900">
        <template v-if="loopKeys.length > 0">
          <el-radio-group v-model="currentLoop" class="mb-2">
            <el-radio-button v-for="key in loopKeys" :key="key" :value="key">
              第 {{ Number(key) + 1 }} 轮
            </el-radio-button>
          </el-radio-group>
          <ExecutionDetailContent :detail="currentLoopDetail" :workflow-mode="workflowMode" />
        </template>
        <template v-else>-</template>
      </div>
    </div>
  </DetailContainer>
</template>
