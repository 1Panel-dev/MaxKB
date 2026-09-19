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
  <el-card shadow="hover" class="border-N300! cursor-pointer" @click="show = !show">
    <MkCollapse v-model:expanded="show" trigger="indicator">
      <template #label>
        <slot name="header" />
      </template>
      <!-- 内容区独立交互，避免链接、表单和嵌套详情点击时收起外层卡片。 -->
      <div v-if="show" class="mt-4 cursor-auto space-y-2" @click.stop>
        <slot v-if="showContent" />
        <div v-else class="mk-gray-card py-2! rounded-xl!">
          <h6 class="mb-2">错误日志</h6>
          <div>{{ data.err_message || '-' }}</div>
        </div>
      </div>
    </MkCollapse>
  </el-card>
</template>
