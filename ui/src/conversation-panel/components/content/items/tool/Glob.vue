<script setup lang="ts">
import { computed } from 'vue'
import type { ChatContent } from '@/api/types'
import { extractPartialJsonFields } from './extract-partial-json'

defineOptions({ name: 'ConversationGlobContent' })

const props = defineProps<{ content: ChatContent; loading: boolean }>()
const expanded = defineModel<boolean>('expanded', { required: true })

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

<template>
  <!-- 展开或收起文件搜索结果 -->
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
        <circle cx="7" cy="7" r="4.5" stroke="currentColor" stroke-width="1.3" />
        <path d="M10.5 10.5L14 14" stroke="currentColor" stroke-width="1.3" stroke-linecap="round" />
        <path d="M7 5v4M5 7h4" stroke="currentColor" stroke-width="1.1" stroke-linecap="round" />
      </svg>
      <span class="min-w-0 max-w-[300px] truncate" :title="pattern || 'glob'">{{ pattern || 'glob' }}</span>
      <span class="tc-param" v-if="dirPath">
        <span class="tc-param-short">{{ dirPath }}/</span>
        <span class="tc-param-full">{{ (args.path || '') + '/' }}</span>
      </span>
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
