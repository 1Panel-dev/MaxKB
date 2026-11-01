<script setup lang="ts">
import { computed } from 'vue'
import type { ChatContent } from '@/api/types'
import { extractPartialJsonField } from './extract-partial-json'

defineOptions({ name: 'ConversationReadFileContent' })

const props = defineProps<{ content: ChatContent; loading: boolean }>()
const expanded = defineModel<boolean>('expanded', { required: true })

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

<template>
  <!-- 展开或收起文件内容 -->
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
        <path d="M4 2h8l2 2v10a1 1 0 0 1-1 1H3a1 1 0 0 1-1-1V3a1 1 0 0 1 1-1Z" stroke="currentColor" stroke-width="1.3" stroke-linejoin="round" />
        <path d="M6 8h4M6 10.5h4M6 5.5h2" stroke="currentColor" stroke-width="1.2" stroke-linecap="round" />
      </svg>
      <span class="min-w-0 max-w-[300px] truncate" :title="filePath || 'read_file'">{{ filePath || 'read_file' }}</span>
      <span class="shrink-0 font-mono text-xs text-N500" v-if="lineCount">{{ lineCount }} lines</span>
    </template>
    <div v-if="parsedLines.length" class="py-1">
      <div class="rf-block">
        <table class="rf-table">
          <tbody>
            <template v-for="(line, i) in parsedLines" :key="i">
              <tr class="rf-row">
                <td class="rf-ln">{{ line.num }}</td>
                <td class="rf-code">
                  <code>{{ line.text || ' ' }}</code>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </div>
  </MkCollapse>
</template>

<style scoped>
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
