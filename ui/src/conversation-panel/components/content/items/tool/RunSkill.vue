<script setup lang="ts">
import { computed } from 'vue'
import type { ChatContent } from '@/api/types'

defineOptions({ name: 'ConversationRunSkillContent' })

const props = defineProps<{ content: ChatContent; loading: boolean }>()
const expanded = defineModel<boolean>('expanded', { required: true })

const args = computed<Record<string, string>>(() => {
  const raw = props.content.arguments
  if (!raw) return {}
  try {
    return JSON.parse(raw) ?? {}
  } catch {
    return {}
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

<template>
  <!-- 展开或收起技能执行结果 -->
  <MkCollapse class="w-full" v-model:expanded="expanded" indicator-position="after" trigger-class="group text-N500! mb-2 w-fit hover:text-N900!">
    <template #indicator="{ expanded }">
      <MkIcon
        name="icon_right_outlined"
        :size="12"
        class="transition-transform text-N500! group-hover:text-N900!"
        :class="{ 'rotate-90': expanded }"
      />
    </template>
    <template #label>
      <span v-if="loading" class="mk-conversation-loading" />
      <svg class="shrink-0" viewBox="0 0 16 16" width="16" height="16" fill="none">
        <path d="M7 8l4 4-4 4" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" stroke-linejoin="round" />
        <path d="M2 12h5" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" />
      </svg>
      <span class="min-w-0 max-w-[300px] truncate" :title="skillLabel">{{ skillLabel }}</span>
    </template>
    <div class="py-1">
      <div class="tc-term-block">
        <div class="tc-term-line cmd">$ {{ commandText }}</div>
        <pre class="tc-term-line out" v-if="content.content">{{ content.content }}</pre>
        <span v-if="loading" class="tc-cursor">▋</span>
      </div>
    </div>
  </MkCollapse>
</template>

<style scoped>
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
