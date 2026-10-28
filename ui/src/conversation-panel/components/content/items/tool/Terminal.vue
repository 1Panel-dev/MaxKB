<template>
  <!-- 展开或收起终端输出 -->
  <MkCollapse
    class="w-full"
    v-model:expanded="expanded"
    trigger-class="group w-fit max-w-full overflow-hidden py-[3px] text-N500 hover:text-N900 transition-colors"
  >
    <template #indicator="{ expanded }">
      <svg class="tc-chevron" :class="{ open: expanded }" viewBox="0 0 16 16" fill="none">
        <path d="M6 4l4 4-4 4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" />
      </svg>
    </template>
    <template #label>
      <span class="tc-icon" :class="{ spin: loading }">
        <Loading v-if="loading" :size="14" />
        <svg v-else viewBox="0 0 16 16" fill="none">
          <path d="M11.5 2.5a1 1 0 0 1 1.4 0l.6.6a1 1 0 0 1 0 1.4l-7.1 7.1-2-2L11.5 2.5ZM4.2 10.2l2 2L3 15l-.7-.7 1.9-4.1Z" fill="currentColor" />
        </svg>
      </span>
      <span class="tc-name" :title="commandText || 'terminal'">{{ commandText || 'terminal' }}</span>
    </template>

    <div class="tc-body">
      <div ref="terminalBlock" class="tc-term-block">
        <div class="tc-term-line cmd">$ {{ commandText }}</div>
        <pre class="tc-term-line out" v-if="content.content">{{ content.content }}</pre>
        <span v-if="loading" class="tc-cursor">▋</span>
      </div>
    </div>
  </MkCollapse>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type { ChatContent } from '@/api/types'
import Loading from '@/conversation-panel/loading/index.vue'
import { extractPartialJsonField } from './extract-partial-json'

defineOptions({ name: 'ConversationTerminalContent' })

const props = defineProps<{ content: ChatContent; loading: boolean }>()
const expanded = defineModel<boolean>('expanded', { required: true })

const commandText = computed(() => {
  const raw = props.content.arguments
  if (!raw) return ''
  return extractPartialJsonField(raw, 'code') || extractPartialJsonField(raw, 'cmd') || raw
})

// 展开后定位到终端输出底部。
const terminalBlock = ref<HTMLElement>()
watch(
  expanded,
  (expanded) => {
    if (expanded && terminalBlock.value) {
      terminalBlock.value.scrollTop = terminalBlock.value.scrollHeight
    }
  },
  { flush: 'post' },
)
</script>

<style scoped>
.tc-chevron {
  width: 14px;
  height: 14px;
  flex-shrink: 0;
  transition: transform 0.15s;
}
.tc-chevron.open {
  transform: rotate(90deg);
}

.tc-icon {
  width: 16px;
  height: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.tc-icon.spin {
  color: var(--mk-N600);
}

.tc-name {
  font-size: 13px;
  font-weight: 500;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  min-width: 0;
  max-width: 400px;
}

.tc-body {
  padding: 6px 0 4px 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.tc-term-block {
  background: #1e1e2e;
  border-radius: 6px;
  padding: 10px 12px;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  font-size: 12.5px;
  line-height: 1.6;
  max-height: 360px;
  overflow-y: auto;
}
.tc-term-line.cmd {
  color: #a6e3a1;
  margin: 0 0 4px;
}
.tc-term-line.out {
  color: #cdd6f4;
  margin: 0;
  white-space: pre-wrap;
  word-break: break-all;
}
.tc-cursor {
  color: #a6e3a1;
  animation: blink 0.8s step-start infinite;
  font-size: 13px;
}
@keyframes blink {
  50% {
    opacity: 0;
  }
}
</style>
