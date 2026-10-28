<template>
  <div class="content-group">
    <!-- 分组头部：标题 + 状态，收起时附当前进展，点击展开/收起组内内容 -->
    <button type="button" class="group-header" @click="isExpanded = !isExpanded">
      <svg class="group-chevron" :class="{ open: isExpanded }" viewBox="0 0 16 16" fill="none">
        <path d="M6 4l4 4-4 4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" />
      </svg>
      <span class="group-name">{{ content.name }}</span>
      <span v-if="!isExpanded && currentActivity" class="group-activity">{{ currentActivity }}</span>
      <span v-if="statusClass" class="group-status" :class="statusClass">{{ statusText }}</span>
    </button>

    <div v-if="isExpanded && childContents.length" class="group-body">
      <ContentList :content-list="childContents" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import ContentList from '@/conversation-panel/components/content-list/index.vue'

/**
 * 通用分组：content.name 为标题，content.status 可选（不传不显示状态），
 * content.children 为任意内容项（可再嵌套 GROUP），交由 ContentList 渲染。
 * 执行中或无状态时默认展开，结束后默认收起，手动切换后以手动为准；收起时展示最新一条子项在做什么。
 */
const props = defineProps<{ content: any }>()

const childContents = computed<any[]>(() => props.content.children ?? [])

const STATUS_TEXT: Record<string, string> = {
  RUNNING: '执行中',
  SUCCESS: '成功',
  FAIL: '失败',
  FAILURE: '失败',
}
const statusText = computed(() => STATUS_TEXT[props.content.status] ?? props.content.status)

const statusClass = computed(() => {
  const status = props.content.status
  if (!status) return ''
  if (status === 'SUCCESS') return 'success'
  if (status === 'FAIL' || status === 'FAILURE') return 'error'
  return 'running'
})

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
function describeChild(child: any): string {
  if (child.type === 'TOOL' || child.type === 'GROUP') return child.name ?? ''
  if (child.type === 'TEXT' || child.type === 'FAILURE') return tail(child.content ?? '')
  if (child.type === 'REASONING') return '思考中'
  return ''
}

// 最新一条子项按 id 排序取最大，与 ContentList 的排序规则一致
const currentActivity = computed(() => {
  const latestChild = childContents.value
    .filter((child) => describeChild(child))
    .reduce<any>((latest, child) => (!latest || (child.id ?? '').localeCompare(latest.id ?? '') >= 0 ? child : latest), undefined)
  return latestChild ? describeChild(latestChild) : ''
})
</script>

<style scoped lang="scss">
.content-group {
  margin-bottom: 8px;
}

.group-header {
  display: flex;
  align-items: center;
  gap: 6px;
  max-width: 100%;
  padding: 4px 0;
  border: none;
  background: none;
  cursor: pointer;
  font-family: inherit;
  font-size: 13px;
  color: var(--t2, #606266);
  text-align: left;
  transition: color 0.15s;
}

.group-header:hover {
  color: var(--t1, #303133);
}

.group-chevron {
  width: 12px;
  height: 12px;
  flex-shrink: 0;
  color: var(--t3, #909399);
  transition: transform 0.15s;
}

.group-chevron.open {
  transform: rotate(90deg);
}

.group-name {
  flex-shrink: 0;
  max-width: 60%;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.group-activity {
  min-width: 0;
  color: var(--t3, #909399);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.group-status {
  flex-shrink: 0;
  font-size: 11px;
  padding: 1px 6px;
  border-radius: 4px;
  background: var(--hv, #f5f7fa);
}

.group-status.success {
  color: #67c23a;
}

.group-status.error {
  color: #f56c6c;
}

.group-status.running {
  color: var(--t3, #909399);
}

.group-body {
  margin: 4px 0 0 5px;
  padding-left: 12px;
  border-left: 2px solid var(--bd, #dcdfe6);
}
</style>
