<script setup lang="ts">
import { computed, type Component } from 'vue'
import { SuccessFilled, CircleCloseFilled, Loading } from '@element-plus/icons-vue'
import { formatTokenNumber } from '@/utils/number'
import { iconComponent } from '@/workflow-canvas/icons/utils'
import type { ExecutionNodeDetail } from './types'

defineOptions({ name: 'BaseHeader' })

const props = defineProps<{
  data: ExecutionNodeDetail
  // 是否显示 tokens 由各节点自行决定；tokens 数值统一由 data 计算。
  showTokens?: boolean
}>()

const nodeIconComponent = computed<Component | null>(() => iconComponent(`${props.data?.type}-icon`))
const isSuccess = computed(() => props.data?.status === 200)
const isRunning = computed(() => props.data?.status === 202)
const tokenCount = computed(() => (props.data?.message_tokens || 0) + (props.data?.answer_tokens || 0))
</script>

<template>
  <div class="flex-between w-full">
    <div class="flex items-center gap-2">
      <component :is="nodeIconComponent" v-if="nodeIconComponent" :size="24" />
      <h6>{{ data.name }}</h6>
    </div>
    <div class="flex items-center gap-3 text-N600">
      <span v-if="showTokens">{{ formatTokenNumber(tokenCount) }} tokens</span>
      <span v-if="!isRunning">{{ data?.run_time?.toFixed(2) || '0.00' }} s</span>

      <MkIcon v-if="isSuccess" :icon="SuccessFilled" class="text-success!" />
      <MkIcon v-else-if="isRunning" :icon="Loading" class="is-loading" />
      <MkIcon v-else :icon="CircleCloseFilled" class="text-danger!" />
    </div>
  </div>
</template>
