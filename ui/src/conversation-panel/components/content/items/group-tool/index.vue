<template>
  <div class="content-group-tool">
    <!-- 分组头部：摘要 + 状态，点击展开/收起组内工具 -->
    <button type="button" class="group-header" @click="isExpanded = !isExpanded">
      <span class="group-name">调用了 {{ toolItems.length }} 个工具</span>
      <span v-if="groupStatus" class="group-status" :class="groupStatus">{{ statusText }}</span>
      <svg class="group-chevron" :class="{ open: isExpanded }" viewBox="0 0 16 16" fill="none">
        <path d="M4 6l4 4 4-4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </button>

    <!-- 组内工具：每个工具一行，可单独展开参数与结果 -->
    <div v-show="isExpanded && toolItems.length" class="group-body">
      <ToolItem v-for="(toolItem, index) in toolItems" :key="toolItem.id ?? index" :tool-item="toolItem" class="group-row" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import ToolItem from './components/ToolItem.vue'

/**
 * 分组工具卡：由 content-list 把相邻 TOOL 折叠而成，content.children 为组内 TOOL 内容项。
 * 状态由组内工具汇总：有执行中为执行中，否则有失败为失败，否则成功。
 * 执行中默认展开，结束后默认收起，手动切换后以手动为准。
 */
const props = defineProps<{ content: any }>()

const toolItems = computed<any[]>(() => props.content.children ?? [])

const groupStatus = computed(() => {
  const childStatuses = toolItems.value.map((toolItem) => toolItem.status)
  if (childStatuses.includes('RUNNING')) return 'running'
  if (childStatuses.some((childStatus) => childStatus === 'FAIL' || childStatus === 'FAILURE')) return 'error'
  return childStatuses.length ? 'success' : ''
})

const STATUS_TEXT: Record<string, string> = { running: '执行中', success: '成功', error: '失败' }
const statusText = computed(() => STATUS_TEXT[groupStatus.value] ?? '')

const manualExpanded = ref<boolean>()
const isExpanded = computed({
  get: () => manualExpanded.value ?? groupStatus.value === 'running',
  set: (value: boolean) => (manualExpanded.value = value),
})
</script>

<style scoped lang="scss">
.content-group-tool {
  margin-bottom: 8px;
}

.group-header {
  display: inline-flex;
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
  transition: color 0.15s;
}

.group-header:hover {
  color: var(--t1, #303133);
}

.group-name {
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

.group-chevron {
  width: 12px;
  height: 12px;
  flex-shrink: 0;
  color: var(--t3, #909399);
  transition: transform 0.15s;
}

.group-chevron:not(.open) {
  transform: rotate(-90deg);
}

.group-body {
  margin-top: 4px;
  background: var(--bg2, #fafafa);
  border: 1px solid var(--bd, #dcdfe6);
  border-radius: 8px;
  overflow: hidden;
}

.group-row + .group-row {
  border-top: 1px solid var(--bd, #ebeef5);
}
</style>
