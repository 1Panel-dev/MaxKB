<template>
  <div class="group-tool-row">
    <!-- 工具行：名称 + 状态，点击展开/收起参数与结果 -->
    <button type="button" class="row-header" @click="isExpanded = !isExpanded">
      <span class="row-name">{{ toolItem.name || 'Tool' }}</span>
      <span v-if="toolItem.status" class="row-status" :class="statusClass">{{ statusText }}</span>
      <svg class="row-chevron" :class="{ open: isExpanded }" viewBox="0 0 16 16" fill="none">
        <path d="M6 4l4 4-4 4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
    </button>

    <div v-show="isExpanded" class="row-body">
      <!-- 请求参数 -->
      <div v-if="toolItem.arguments" class="row-section">
        <div class="row-section-title">参数</div>
        <pre class="row-code">{{ formattedArguments }}</pre>
      </div>
      <!-- 返回结果 -->
      <div v-if="toolItem.content" class="row-section">
        <div class="row-section-title">结果</div>
        <pre class="row-code">{{ formattedResult }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

/** 分组工具卡表格中的一行，字段与 TOOL 内容项一致（name / arguments / content / status）。 */
const props = defineProps<{ toolItem: any }>()

const isExpanded = ref(false)

const STATUS_TEXT: Record<string, string> = {
  RUNNING: '执行中',
  SUCCESS: '成功',
  FAIL: '失败',
  FAILURE: '失败',
}
const statusText = computed(() => STATUS_TEXT[props.toolItem.status] ?? props.toolItem.status)

const statusClass = computed(() => {
  const status = props.toolItem.status
  if (status === 'SUCCESS') return 'success'
  if (status === 'FAIL' || status === 'FAILURE') return 'error'
  return 'running'
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

<style scoped lang="scss">
.row-header {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 8px 12px;
  border: none;
  background: none;
  cursor: pointer;
  font-family: inherit;
  font-size: 13px;
  color: var(--t1, #303133);
  text-align: left;
  transition: background 0.15s;
}

.row-header:hover {
  background: var(--hv, #f5f7fa);
}

.row-name {
  min-width: 0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.row-status {
  flex-shrink: 0;
  font-size: 11px;
  padding: 1px 6px;
  border-radius: 4px;
  background: var(--hv, #f5f7fa);
}

.row-status.success {
  color: #67c23a;
}

.row-status.error {
  color: #f56c6c;
}

.row-status.running {
  color: var(--t3, #909399);
}

.row-chevron {
  width: 12px;
  height: 12px;
  flex-shrink: 0;
  color: var(--t3, #909399);
  transition: transform 0.15s;
}

.row-chevron.open {
  transform: rotate(90deg);
}

.row-body {
  padding: 0 12px 10px;
}

.row-section + .row-section {
  margin-top: 8px;
}

.row-section-title {
  font-size: 11px;
  font-weight: 500;
  color: var(--t3, #909399);
  margin-bottom: 4px;
}

.row-code {
  margin: 0;
  padding: 8px 10px;
  border-radius: 6px;
  background: var(--hv, #f5f7fa);
  border: 1px solid var(--bd, #ebeef5);
  font-size: 12px;
  line-height: 1.6;
  color: var(--t1, #303133);
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 320px;
  overflow: auto;
}
</style>
