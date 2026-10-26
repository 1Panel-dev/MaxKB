<template>
  <div class="content-tool">
    <!-- 工具调用头部：函数名 + 状态，点击展开/收起 -->
    <button type="button" class="tool-header" @click="isExpanded = !isExpanded">
      <svg class="tool-chevron" :class="{ open: isExpanded }" viewBox="0 0 16 16" fill="none">
        <path d="M6 4l4 4-4 4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      <svg class="tool-icon" width="14" height="14" viewBox="0 0 14 14" fill="none">
        <path d="M10.5 2.5h-7a1 1 0 00-1 1v7a1 1 0 001 1h7a1 1 0 001-1v-7a1 1 0 00-1-1z" stroke="currentColor" stroke-width="1.2"/>
        <path d="M5.5 5.5h3M5.5 8h3" stroke="currentColor" stroke-width="1.2" stroke-linecap="round"/>
      </svg>
      <span class="tool-name">{{ content.name || 'Tool' }}</span>
      <span v-if="content.status" class="tool-status" :class="statusClass">{{ statusText }}</span>
    </button>

    <div v-show="isExpanded" class="tool-body">
      <!-- 请求参数 -->
      <div v-if="content.arguments" class="tool-section">
        <div class="tool-section-title">参数</div>
        <pre class="tool-code">{{ formattedArguments }}</pre>
      </div>
      <!-- 返回结果 -->
      <div v-if="content.content" class="tool-section">
        <div class="tool-section-title">结果</div>
        <pre class="tool-code">{{ formattedResult }}</pre>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'

const props = defineProps<{ content: any }>()

const isExpanded = ref(false)

// 状态文案与配色
const statusText = computed(() => {
  const map: Record<string, string> = {
    RUNNING: '执行中',
    SUCCESS: '成功',
    FAIL: '失败',
    FAILURE: '失败',
  }
  return map[props.content.status] ?? props.content.status
})

const statusClass = computed(() => {
  const status = props.content.status
  if (status === 'SUCCESS') return 'success'
  if (status === 'FAIL' || status === 'FAILURE') return 'error'
  return 'running'
})

// 参数为 JSON 字符串，尝试格式化展示，失败则原样展示
function tryFormatJson(value: any): string {
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

<style scoped lang="scss">
.content-tool {
  background: var(--bg2, #fafafa);
  border: 1px solid var(--bd, #dcdfe6);
  border-radius: 8px;
  overflow: hidden;
  margin-bottom: 8px;
}

.tool-header {
  display: flex;
  align-items: center;
  gap: 6px;
  width: 100%;
  padding: 8px 12px;
  border: none;
  background: none;
  cursor: pointer;
  font-family: inherit;
  font-size: 12px;
  color: var(--t2, #606266);
  transition: color 0.15s;
}

.tool-header:hover {
  color: var(--t1, #303133);
}

.tool-chevron {
  width: 12px;
  height: 12px;
  flex-shrink: 0;
  color: var(--t3, #909399);
  transition: transform 0.15s;
}

.tool-chevron.open {
  transform: rotate(90deg);
}

.tool-icon {
  flex-shrink: 0;
}

.tool-name {
  font-weight: 500;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.tool-status {
  margin-left: auto;
  flex-shrink: 0;
  font-size: 11px;
  padding: 1px 6px;
  border-radius: 4px;
  background: var(--hv, #f5f7fa);
}

.tool-status.success {
  color: #67c23a;
}

.tool-status.error {
  color: #f56c6c;
}

.tool-status.running {
  color: var(--t3, #909399);
}

.tool-body {
  padding: 0 12px 10px;
}

.tool-section + .tool-section {
  margin-top: 8px;
}

.tool-section-title {
  font-size: 11px;
  font-weight: 500;
  color: var(--t3, #909399);
  margin-bottom: 4px;
}

.tool-code {
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
