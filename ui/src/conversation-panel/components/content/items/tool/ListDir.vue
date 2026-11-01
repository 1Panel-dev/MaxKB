<script setup lang="ts">
import { computed } from 'vue'
import type { ChatContent } from '@/api/types'
import { extractPartialJsonField } from './extract-partial-json'

defineOptions({ name: 'ConversationListDirContent' })

const props = defineProps<{ content: ChatContent; loading: boolean }>()
const expanded = defineModel<boolean>('expanded', { required: true })

const dirPath = computed(() => {
  const raw = props.content.arguments
  if (!raw) return ''
  return extractPartialJsonField(raw, 'path')
})
const summary = computed(() => props.content.summary || '')
</script>

<template>
  <!-- 展开或收起目录内容 -->
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
        <path
          d="M2 4.5A1.5 1.5 0 0 1 3.5 3h2.086a1.5 1.5 0 0 1 1.06.44l.354.354a.5.5 0 0 0 .354.146H12.5A1.5 1.5 0 0 1 14 5.44V11.5a1.5 1.5 0 0 1-1.5 1.5h-9A1.5 1.5 0 0 1 2 11.5v-7Z"
          stroke="currentColor"
          stroke-width="1.3"
          stroke-linejoin="round"
        />
      </svg>
      <span class="min-w-0 max-w-[300px] truncate" :title="dirPath || 'list_dir'">{{ dirPath || 'list_dir' }}</span>
      <span class="shrink-0 font-mono text-xs text-N500" v-if="summary">{{ summary }}</span>
    </template>
    <div v-if="content.content" class="py-1">
      <div class="rf-block">
        <pre class="rf-content">{{ content.content }}</pre>
      </div>
    </div>
  </MkCollapse>
</template>

<style scoped>
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
  line-height: 1.6;
  color: var(--mk-N900);
  white-space: pre;
}
</style>
