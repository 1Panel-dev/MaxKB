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
  <el-card shadow="never">
    <MkCollapse v-model:expanded="show" trigger-class="py-0!">
      <template #label>
        <slot name="header" />
      </template>
      <div v-if="show" class="mt-4 space-y-2">
        <slot v-if="showContent" />
        <div v-else class="mk-gray-card py-2! rounded-xl!">
          <h6 class="mb-2">错误日志</h6>
          <div>{{ data.err_message || '-' }}</div>
        </div>
      </div>
    </MkCollapse>
  </el-card>
</template>
