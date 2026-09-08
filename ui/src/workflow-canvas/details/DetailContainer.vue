<script setup lang="ts">
import { computed, ref } from 'vue'
import type { ExecutionNodeDetail } from './types'

defineOptions({ name: 'DetailContainer' })

const props = withDefaults(
  defineProps<{
    data: ExecutionNodeDetail
    // 循环等节点即使整体失败也需展示已执行的子节点详情，其余节点失败时只展示错误日志。
    showContentOnError?: boolean
  }>(),
  {
    showContentOnError: false,
  },
)

const show = ref(false)
const isSuccess = computed(() => props.data?.status === 200)
const showContent = computed(() => isSuccess.value || props.showContentOnError)
</script>

<template>
  <el-card class="execution-detail-card mb-2" shadow="never" style="--el-card-padding: 8px 12px">
    <div class="cursor-pointer" @click="show = !show">
      <slot name="header" :show="show" />
    </div>
    <el-collapse-transition>
      <div v-if="show" class="mt-3 flex flex-col gap-2">
        <slot v-if="showContent" />
        <div v-else class="overflow-hidden rounded-md bg-N100">
          <h5 class="px-3 py-2">错误日志</h5>
          <div class="border-t border-dashed px-3 py-2 text-N900">{{ data.err_message || '-' }}</div>
        </div>
      </div>
    </el-collapse-transition>
  </el-card>
</template>
