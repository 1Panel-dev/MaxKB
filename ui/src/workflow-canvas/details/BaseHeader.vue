<script setup lang="ts">
import { computed, type Component } from 'vue'
import { CaretRight, CircleCheck, CircleClose, Loading } from '@element-plus/icons-vue'
import { iconComponent } from '@/workflow-canvas/icons/utils'
import type { ExecutionNodeDetail } from './types'

defineOptions({ name: 'BaseHeader' })

const props = defineProps<{
  data: ExecutionNodeDetail
  show?: boolean
  // 是否显示 tokens 由各节点自行决定；tokens 数值统一由 data 计算。
  showTokens?: boolean
}>()

const nodeIconComponent = computed<Component | null>(() => iconComponent(`${props.data?.type}-icon`))
const isSuccess = computed(() => props.data?.status === 200)
const isRunning = computed(() => props.data?.status === 202)
const tokenCount = computed(() => (props.data?.message_tokens || 0) + (props.data?.answer_tokens || 0))
</script>

<template>
  <div class="flex-between">
    <div class="flex items-center gap-2">
      <el-icon class="text-N600 transition-transform" :class="{ 'rotate-90': show }">
        <CaretRight />
      </el-icon>
      <component :is="nodeIconComponent" v-if="nodeIconComponent" :size="24" />
      <h4>{{ data.name }}</h4>
    </div>
    <div class="flex items-center gap-3 text-N600">
      <span v-if="showTokens">{{ tokenCount }} tokens</span>
      <span v-if="!isRunning">{{ data?.run_time?.toFixed(2) || '0.00' }} s</span>
      <el-icon v-if="isSuccess" class="text-success" :size="16">
        <CircleCheck />
      </el-icon>
      <el-icon v-else-if="isRunning" class="is-loading text-primary" :size="16">
        <Loading />
      </el-icon>
      <el-icon v-else class="text-danger" :size="16">
        <CircleClose />
      </el-icon>
    </div>
  </div>
</template>
