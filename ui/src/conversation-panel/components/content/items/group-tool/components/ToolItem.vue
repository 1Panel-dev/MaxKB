<script setup lang="ts">
import { computed, ref } from 'vue'
import type { ChatContent, Dict } from '@/api/types'

defineOptions({ name: 'ConversationGroupToolItem' })

const props = defineProps<{ toolItem: ChatContent }>()

// 分组内默认工具独立展开，初始收起。
const isExpanded = ref(false)
const loading = computed(() => props.toolItem.status === 'RUNNING')
const toolTitle = computed(() => props.toolItem.name || 'Tool')

const STATUS_TEXT: Dict<string> = {
  RUNNING: '执行中',
  SUCCESS: '成功',
  FAIL: '失败',
  FAILURE: '失败',
}
const statusText = computed(() => {
  const status = props.toolItem.status ?? ''
  return STATUS_TEXT[status] ?? status
})

const statusType = computed(() => {
  const status = props.toolItem.status
  if (status === 'SUCCESS') return 'success'
  if (status === 'FAIL' || status === 'FAILURE') return 'danger'
  return 'info'
})

// 参数为 JSON 字符串，尝试格式化展示，失败则原样展示
function tryFormatJson(value: unknown): string {
  if (value == null) return ''
  if (typeof value !== 'string') {
    try {
      return JSON.stringify(value, null, 2)
    } catch {
      return String(value)
    }
  }
  try {
    return JSON.stringify(JSON.parse(value), null, 2)
  } catch {
    return value
  }
}

const formattedArguments = computed(() => tryFormatJson(props.toolItem.arguments ?? ''))
const formattedResult = computed(() => tryFormatJson(props.toolItem.content))
</script>

<template>
  <!-- 展开或收起分组内工具参数 -->
  <MkCollapse class="w-full" v-model:expanded="isExpanded" indicator-position="after" trigger-class="group text-N500! mb-2 w-fit hover:text-N900!">
    <template #indicator="{ expanded }">
      <MkIcon
        name="icon_right_outlined"
        :size="12"
        class="transition-transform text-N500! group-hover:text-N900!"
        :class="{ 'rotate-90': expanded }"
      />
    </template>
    <template #label>
      <span v-if="loading" class="mk-conversation-loading" />
      <MkIcon name="icon_busy_outlined" />
      <span class="min-w-0 max-w-[300px] truncate" :title="toolTitle">{{ toolTitle }}</span>
      <el-tag v-if="toolItem.status" size="small" :type="statusType">{{ statusText }}</el-tag>
    </template>

    <div class="space-y-2 pb-2">
      <!-- 请求参数 -->
      <div v-if="toolItem.arguments" class="mk-gray-card-lg py-3!">
        <h6 class="mb-2">输入参数</h6>
        <div class="whitespace-pre-wrap break-words">{{ formattedArguments }}</div>
      </div>
      <!-- 返回结果 -->
      <div v-if="toolItem.content" class="mk-gray-card-lg py-3!">
        <h6 class="mb-2">输出参数</h6>
        <div class="whitespace-pre-wrap break-words">{{ formattedResult }}</div>
      </div>
    </div>
  </MkCollapse>
</template>
