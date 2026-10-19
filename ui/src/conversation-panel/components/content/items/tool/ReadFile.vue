<template>
  <div class="tool-call">
    <button class="tc-head" @click="$emit('toggle')">
      <svg class="tc-chevron" :class="{ open: expanded }" viewBox="0 0 16 16" fill="none">
        <path d="M6 4l4 4-4 4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" />
      </svg>
      <span class="tc-icon" :class="{ spin: loading }">
        <Loading v-if="loading" :size="14" />
        <svg v-else viewBox="0 0 16 16" width="16" height="16" fill="none">
          <path d="M4 2h8l2 2v10a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V3a1 1 0 0 1 1-1Z" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round" />
          <path d="M6 8h4M6 10.5h4M6 5.5h2" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" />
        </svg>
      </span>
      <span class="tc-name">{{ filePath || 'read_file' }}</span>
      <span class="tc-lines" v-if="lineCount">{{ lineCount }} lines</span>
    </button>

    <Transition enter-active-class="tc-expand-enter" leave-active-class="tc-expand-leave">
      <div v-if="expanded && parsedLines.length" class="tc-body">
        <div class="rf-block">
          <table class="rf-table">
            <tbody>
              <tr v-for="(line, i) in parsedLines" :key="i" class="rf-row">
                <td class="rf-ln">{{ line.num }}</td>
                <td class="rf-code">
                  <code>{{ line.text || ' ' }}</code>
                </td>
              </tr>
            </tbody>
          </table>
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

const filePath = computed(() => {
  const raw = props.content.arguments
  if (!raw) return ''
  return extractPartialJsonField(raw, 'path')
})

const parsedLines = computed(() => {
  const raw = props.content.content
  if (!raw) return []
  return raw.split('\n').map((line: string) => {
    const idx = line.indexOf('→')
    if (idx > 0) {
      return { num: line.substring(0, idx).trim(), text: line.substring(idx + 1) }
    }
    return { num: '', text: line }
  })
})

const lineCount = computed(() => parsedLines.value.length)
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
  overflow: hidden;
  max-height: 360px;
  overflow-y: auto;
}

.rf-table {
  width: 100%;
  border-collapse: collapse;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  font-size: 12px;
  line-height: 1.55;
}

.rf-row {
  height: 22px;
}

.rf-ln {
  width: 40px;
  min-width: 40px;
  padding: 0 8px 0 10px;
  color: var(--mk-N500);
  text-align: right;
  user-select: none;
  vertical-align: top;
  border-right: 1px solid var(--mk-N300);
}

.rf-code {
  padding: 0 12px;
  white-space: pre-wrap;
  word-break: break-all;
  color: var(--mk-N900);
  vertical-align: top;
}
.rf-code code {
  display: inline;
  color: inherit;
  font: inherit;
  white-space: pre-wrap;
  word-break: break-all;
}
</style>
