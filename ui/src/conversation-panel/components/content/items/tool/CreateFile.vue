<template>
  <div class="tool-call">
    <button class="tc-head" @click="$emit('toggle')">
      <svg class="tc-chevron" :class="{ open: expanded }" viewBox="0 0 16 16" fill="none">
        <path d="M6 4l4 4-4 4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" />
      </svg>
      <span class="tc-icon" :class="{ spin: loading }">
        <Loading v-if="loading" :size="14" />
        <svg v-else viewBox="0 0 16 16" width="16" height="16" fill="none">
          <path d="M9 2H4a1 1 0 0 0-1 1v10a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1V6L9 2Z" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round" />
          <path d="M8 7.5v4M6 9.5h4" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" />
        </svg>
      </span>
      <span class="tc-name">{{ title }}</span>
      <span v-if="fileInfo" class="tc-stat add">+{{ fileInfo.additions }}</span>
    </button>

    <Transition enter-active-class="tc-expand-enter" leave-active-class="tc-expand-leave">
      <div v-if="expanded" class="tc-body">
        <ScrollDiff v-if="fileInfo" :file="fileInfo" />
        <div v-else-if="loading" class="tc-loading-dots">
          <span></span>
          <span></span>
          <span></span>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import Loading from '@/conversation-panel/loading/index.vue'
import ScrollDiff from './components/ScrollDiff.vue'
import type { PatchFileInfo } from './patch/patchTypes'
import { extractPartialJsonField } from './extract-partial-json'

const props = defineProps<{ content: any; loading: boolean; expanded: boolean }>()
defineEmits<{ toggle: [] }>()

const filePath = computed(() => {
  return extractPartialJsonField(props.content.arguments, 'path')
})

const fileContent = computed(() => {
  return extractPartialJsonField(props.content.arguments, 'content')
})

const title = computed(() => {
  return filePath.value ? `create ${filePath.value}` : 'create_file'
})

const fileInfo = computed<PatchFileInfo | null>(() => {
  if (!fileContent.value) return null
  const path = filePath.value || 'unknown'
  const lines = fileContent.value.split('\n')
  return {
    status: 'add',
    oldPath: path,
    newPath: path,
    additions: lines.length,
    deletions: 0,
    isBinary: false,
    lines: lines.map((line, i) => ({
      type: 'add' as const,
      oldLineNumber: null,
      newLineNumber: i + 1,
      displayLineNumber: i + 1,
      prefix: '+',
      content: line,
      raw: `+${line}`,
    })),
  }
})
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

.tc-stat {
  font-size: 11px;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  flex-shrink: 0;
}
.tc-stat.add {
  color: #16a34a;
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
    max-height: 800px;
  }
}
@keyframes tc-close {
  from {
    opacity: 1;
    max-height: 800px;
  }
  to {
    opacity: 0;
    max-height: 0;
  }
}

.tc-body {
  padding: 6px 0 4px 8px;
}

.tc-loading-dots {
  display: flex;
  gap: 4px;
  padding: 4px 2px;
}
.tc-loading-dots span {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: var(--mk-N500);
  animation: dot-pulse 1.2s ease-in-out infinite;
}
.tc-loading-dots span:nth-child(2) {
  animation-delay: 0.2s;
}
.tc-loading-dots span:nth-child(3) {
  animation-delay: 0.4s;
}
@keyframes dot-pulse {
  0%,
  80%,
  100% {
    opacity: 0.3;
    transform: scale(0.8);
  }
  40% {
    opacity: 1;
    transform: scale(1);
  }
}
</style>
