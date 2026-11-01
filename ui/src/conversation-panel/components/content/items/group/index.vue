<script setup lang="ts">
import { computed, ref } from 'vue'
import type { ChatContent } from '@/api/types'
import ContentList from '@/conversation-panel/components/content-list/index.vue'

/**
 * 通用分组：content.name 为标题，content.status 可选（不传不显示状态），
 * content.children 为任意内容项（可再嵌套 GROUP），交由 ContentList 渲染。
 * 执行中或无状态时默认展开，结束后默认收起，手动切换后以手动为准；收起时展示最新一条子项在做什么。
 */
defineOptions({ name: 'ConversationGroupContent' })

const props = defineProps<{ content: ChatContent }>()

const childContents = computed(() => props.content.children ?? [])

const STATUS_TEXT: Record<string, string> = {
  RUNNING: '执行中',
  SUCCESS: '成功',
  FAIL: '失败',
  FAILURE: '失败',
}
const statusText = computed(() => STATUS_TEXT[props.content.status ?? ''] ?? props.content.status)

const statusType = computed(() => {
  const status = props.content.status
  if (status === 'SUCCESS') return 'success'
  if (status === 'FAIL' || status === 'FAILURE') return 'danger'
  return 'info'
})

const isFailed = computed(() => props.content.status === 'FAIL' || props.content.status === 'FAILURE')

const manualExpanded = ref<boolean>()
const isExpanded = computed({
  get: () => manualExpanded.value ?? (!props.content.status || props.content.status === 'RUNNING'),
  set: (value: boolean) => (manualExpanded.value = value),
})

function tail(text: string) {
  const trimmed = text.trim()
  return trimmed.length > 40 ? `…${trimmed.slice(-40)}` : trimmed
}

// 子项在做什么：工具取名称，正文取末尾，思考固定文案，子分组取标题，失败取错误信息
function describeChild(child: ChatContent): string {
  if (child.type === 'TOOL' || child.type === 'GROUP') return child.name ?? ''
  if (child.type === 'TEXT' || child.type === 'FAILURE') return tail(child.content ?? '')
  if (child.type === 'REASONING') return '思考中'
  return ''
}

// 最新一条子项按 id 排序取最大，与 ContentList 的排序规则一致
const currentActivity = computed(() => {
  const latestChild = childContents.value
    .filter((child) => describeChild(child))
    .reduce<ChatContent | undefined>((latest, child) => (!latest || (child.id ?? '').localeCompare(latest.id ?? '') >= 0 ? child : latest), undefined)
  return latestChild ? describeChild(latestChild) : ''
})
</script>

<template>
  <!-- 展开或收起分组内容 -->
  <MkCollapse
    class="mb-2 w-full"
    v-model:expanded="isExpanded"
    indicator-position="after"
    trigger-class="group text-N500! mb-2 w-fit max-w-full hover:text-N900!"
  >
    <template #indicator="{ expanded }">
      <MkIcon
        name="icon_right_outlined"
        :size="12"
        class="transition-transform text-N500! group-hover:text-N900!"
        :class="{ 'rotate-90': expanded }"
      />
    </template>
    <template #label>
      <span v-if="content.status === 'RUNNING'" class="mk-conversation-loading" />
      <span class="min-w-0 max-w-[300px] truncate" :title="content.name">{{ content.name }}</span>
      <span v-if="!isExpanded && currentActivity" class="min-w-0 truncate" :title="currentActivity">{{ currentActivity }}</span>
      <el-tag v-if="isFailed" size="small" :type="statusType">{{ statusText }}</el-tag>
    </template>

    <div v-if="isExpanded && childContents.length" class="mt-1 border-l-2 border-N900/15 pl-3">
      <ContentList :content-list="childContents" />
    </div>
  </MkCollapse>
</template>
