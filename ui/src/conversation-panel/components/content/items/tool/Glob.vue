<template>
  <div class="tool-call">
    <button class="tc-head" @click="$emit('toggle')">
      <svg class="tc-chevron" :class="{ open: expanded }" viewBox="0 0 16 16" fill="none">
        <path d="M6 4l4 4-4 4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" />
      </svg>
      <span class="tc-icon" :class="{ spin: loading }">
        <Loading v-if="loading" :size="14" />
        <svg v-else viewBox="0 0 16 16" width="16" height="16" fill="none">
          <circle cx="7" cy="7" r="4.5" stroke="currentColor" stroke-width="1.3" />
          <path d="M10.5 10.5L14 14" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" />
          <path d="M7 5v4M5 7h4" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" />
        </svg>
      </span>
      <span class="tc-name">{{ pattern || 'glob' }}</span>
      <span class="tc-param" v-if="dirPath">
        <span class="tc-param-short">{{ dirPath }}/</span>
        <span class="tc-param-full">{{ (args.path || '') + '/' }}</span>
      </span>
      <span class="tc-lines" v-if="summary">{{ summary }}</span>
    </button>

    <Transition enter-active-class="tc-expand-enter" leave-active-class="tc-expand-leave">
      <div v-if="expanded && content.content" class="tc-body">
        <div class="rf-block">
          <pre class="rf-content">{{ content.content }}</pre>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import Loading from '@/conversation-panel/loading/index.vue'
import { extractPartialJsonFields } from './extract-partial-json'

const props = defineProps<{ content: any; loading: boolean; expanded: boolean }>()
defineEmits<{ toggle: [] }>()

const args = computed(() => {
  const raw = props.content.arguments
  if (!raw) return {} as Record<string, string>
  return extractPartialJsonFields(raw, ['pattern', 'path'])
})

const pattern = computed(() => args.value.pattern || '')
const dirPath = computed(() => {
  const p = args.value.path || ''
  if (!p) return ''
  // 路径太长只保留最后两级
  const parts = p.replace(/\/$/, '').split('/')
  return parts.length > 2 ? '.../' + parts.slice(-2).join('/') : p
})
const summary = computed(() => props.content.summary || '')
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
}

.tc-param {
  font-size: 11px;
  color: var(--mk-N500);
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  flex-shrink: 1;
  min-width: 0;
  overflow: hidden;
  cursor: default;
}

.tc-param-full {
  display: none;
}

.tc-param:hover .tc-param-short {
  display: none;
}

.tc-param:hover .tc-param-full {
  display: inline;
}

.tc-lines {
  font-size: 11px;
  color: var(--mk-N500);
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  flex-shrink: 0;
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
  padding: 4px 0;
}

.rf-block {
  background: var(--mk-N100);
  border: 1px solid var(--mk-N300);
  border-radius: 6px;
  padding: 8px 12px;
  max-height: 360px;
  overflow-y: auto;
}

.rf-content {
  margin: 0;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  font-size: 12px;
  line-height: 1.5;
  color: var(--mk-N900);
  white-space: pre-wrap;
  word-break: break-all;
}
</style>
