<template>
  <!-- 展开或收起终端输出 -->
  <MkCollapse class="w-full" v-model:expanded="expanded" indicatorPosition="after" trigger-class="group text-N500! mb-2 w-fit hover:text-N900!">
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
      <MkIcon name="icon_command_outlined"></MkIcon>
      <span :title="commandText || 'terminal'" class="min-w-0 max-w-[300px] truncate">{{ commandText || 'terminal' }}</span>
    </template>

    <div ref="terminalBlock" class="tc-terminal-block">
      <div class="cmd">$ {{ commandText }}</div>
      <pre class="out" v-if="content.content">{{ content.content }}</pre>
      <span v-if="loading" class="tc-cursor">▋</span>
    </div>
  </MkCollapse>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import type { ChatContent } from '@/api/types'
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

<style scoped lang="scss">
.tc-terminal-block {
  background: #211d2f;
  border-radius: 12px;
  padding: 12px 16px;
  font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, monospace;
  font-size: 12px;
  max-height: 360px;
  overflow-y: auto;
  .cmd {
    color: #a6e3a1;
  }
  .out {
    color: white;
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
}
</style>
