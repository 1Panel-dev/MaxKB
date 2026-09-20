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

// 每一轮循环的子节点执行详情，键为轮次下标。
const loopKeys = computed(() => Object.keys(props.data?.loop_node_data || {}))
const currentLoop = ref(loopKeys.value[0] ?? '')

// 当前选中轮次的子节点数组，交回顶层 dispatcher 递归渲染（其内部已按 index 排序、按类型分发）。
const currentLoopDetail = computed<ExecutionNodeDetail[]>(() => Object.values(props.data?.loop_node_data?.[currentLoop.value] || {}))
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
        <p><span class="text-N600">循环类型：</span>{{ data.loop_type || '-' }}</p>
        <p>
          <span class="text-N600">循环数组：</span>
          {{ data.loop_type === 'NUMBER' ? data.number : loopKeys.join(', ') || '-' }}
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
