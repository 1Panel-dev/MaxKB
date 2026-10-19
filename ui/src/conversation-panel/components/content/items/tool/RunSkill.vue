<template>
  <div class="tool-call">
    <button class="tc-head" @click="$emit('toggle')">
      <svg class="tc-chevron" :class="{ open: expanded }" viewBox="0 0 16 16" fill="none">
        <path d="M6 4l4 4-4 4" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" />
      </svg>
      <span class="tc-icon" :class="{ spin: loading }">
        <Loading v-if="loading" :size="14" />
        <svg v-else viewBox="0 0 16 16" width="16" height="16" fill="none">
          <path d="M7 8l4 4-4 4" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" />
          <path d="M2 12h5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" />
        </svg>
      </span>
      <span class="tc-name">{{ skillLabel }}</span>
    </button>

    <Transition enter-active-class="tc-expand-enter" leave-active-class="tc-expand-leave">
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

const props = defineProps<{ content: any; loading: boolean; expanded: boolean }>()
defineEmits<{ toggle: [] }>()

const args = computed(() => {
  const raw = props.content.arguments
  if (!raw) return {} as any
  try {
    return JSON.parse(raw)
  } catch {
    return {} as any
  }
})

const skillLabel = computed(() => {
  const skillId = args.value.skill_id || ''
  const command = args.value.command || ''
  if (skillId && command) return `${skillId}: ${command}`
  if (skillId) return skillId
  return 'run_skill'
})

const commandText = computed(() => args.value.command || '')
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
