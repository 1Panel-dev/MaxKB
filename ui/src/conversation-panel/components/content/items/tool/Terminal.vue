<template>
  <div class="tool-call">
    <button class="tc-head" @click="$emit('toggle')">
      <svg class="tc-chevron" :class="{ open: expanded }" viewBox="0 0 16 16" fill="none">
        <path d="M6 4l4 4-4 4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" />
      </svg>
      <span class="tc-icon" :class="{ spin: loading }">
        <Loading v-if="loading" :size="14" />
        <svg v-else viewBox="0 0 16 16" fill="none">
          <path d="M11.5 2.5a1 1 0 0 1 1.4 0l.6.6a1 1 0 0 1 0 1.4l-7.1 7.1-2-2L11.5 2.5ZM4.2 10.2l2 2L3 15l-.7-.7 1.9-4.1Z" fill="currentColor" />
        </svg>
      </span>
      <span class="tc-name">{{ commandText || 'terminal' }}</span>
    </button>

    <Transition enter-active-class="tc-expand-enter" leave-active-class="tc-expand-leave" @after-enter="onAfterEnter">
      <div v-if="expanded" class="tc-body">
        <div class="tc-term-block">
          <div class="tc-term-line cmd">$ {{ commandText }}</div>
          <pre class="tc-term-line out" v-if="content.content">{{ content.content }}</pre>
          <span v-if="loading" class="tc-cursor">▋</span>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import Loading from '@/conversation-panel/loading/index.vue'
import { extractPartialJsonField } from './extract-partial-json'

const props = defineProps<{ content: any; loading: boolean; expanded: boolean }>()
defineEmits<{ toggle: [] }>()

const commandText = computed(() => {
  const raw = props.content.arguments
  if (!raw) return ''
  return extractPartialJsonField(raw, 'command') || extractPartialJsonField(raw, 'cmd') || raw
})

const onAfterEnter = (el: Element) => {
  const termBlock = (el as HTMLElement).querySelector('.tc-term-block')
  if (termBlock) termBlock.scrollTop = termBlock.scrollHeight
}
</script>

<style scoped>
.tool-call {
  width: 100%;
}

.tc-head {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 3px 0;
  border: none;
  background: none;
  cursor: pointer;
  font-family: inherit;
  color: var(--mk-N500);
  transition: color 0.15s;
  max-width: 100%;
  overflow: hidden;
}
.tc-head:hover {
  color: var(--mk-N900);
}

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

.tc-expand-enter {
  animation: tc-open 0.2s ease-out;
  overflow: hidden;
}
.tc-expand-leave {
  animation: tc-close 0.15s ease-in forwards;
  overflow: hidden;
}
@keyframes tc-open {
  from {
    opacity: 0;
    max-height: 0;
  }
  to {
    opacity: 1;
    max-height: 600px;
  }
}
@keyframes tc-close {
  from {
    opacity: 1;
    max-height: 600px;
  }
  to {
    opacity: 0;
    max-height: 0;
  }
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
