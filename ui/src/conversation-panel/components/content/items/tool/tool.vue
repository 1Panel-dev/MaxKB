<script setup lang="ts">
import { computed, ref } from 'vue'
import type { ChatContent, Dict } from '@/api/types'

defineOptions({ name: 'ConversationDefaultToolContent' })

const props = defineProps<{ content: ChatContent }>()

// 默认工具独立管理展开状态，初始收起。
const isExpanded = ref(false)
const loading = computed(() => props.content.status === 'RUNNING')
const toolTitle = computed(() => props.content.name || 'Tool')

// 状态文案与配色
const statusText = computed(() => {
  const map: Dict<string> = {
    RUNNING: '执行中',
    SUCCESS: '成功',
    FAIL: '失败',
    FAILURE: '失败',
  }
  const status = props.content.status ?? ''
  return map[status] ?? status
})

const statusType = computed(() => {
  const status = props.content.status
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

// arguments 为 None/undefined 时归一为空字符串
const formattedArguments = computed(() => tryFormatJson(props.content.arguments ?? ''))
// 结果对应后端 content 字段（tool_content.py：self.content = result）
const formattedResult = computed(() => tryFormatJson(props.content.content))
</script>

<template>
  <!-- 展开或收起工具调用内容 -->
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
      <el-tag v-if="content.status" size="small" :type="statusType">{{ statusText }}</el-tag>
    </template>

    <div class="space-y-2">
      <!-- 请求参数 -->
      <div v-if="content.arguments" class="mk-gray-card-lg py-3!">
        <h6 class="mb-2">输入参数</h6>
        <div class="whitespace-pre-wrap break-words">{{ formattedArguments }}</div>
      </div>
      <!-- 返回结果 -->
      <div v-if="content.content" class="mk-gray-card-lg py-3!">
        <h6 class="mb-2">输出参数</h6>
        <div class="whitespace-pre-wrap break-words">{{ formattedResult }}</div>
      </div>
    </div>
  </MkCollapse>
</template>
