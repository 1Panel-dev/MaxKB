<script setup lang="ts">
import { computed } from 'vue'
import type { ChatContent } from '@/api/types'
import ScrollDiff from './components/ScrollDiff.vue'
import type { PatchFileInfo } from './patch/patchTypes'
import { extractPartialJsonField } from './extract-partial-json'

defineOptions({ name: 'ConversationCreateFileContent' })

const props = defineProps<{ content: ChatContent; loading: boolean }>()
const expanded = defineModel<boolean>('expanded', { required: true })

// 从流式参数中提取文件路径和内容。
const filePath = computed(() => extractPartialJsonField(props.content.arguments, 'path'))

const fileContent = computed(() => extractPartialJsonField(props.content.arguments, 'content'))

const title = computed(() => (filePath.value ? `create ${filePath.value}` : 'create_file'))

// 将新文件内容转换为新增差异行，供差异组件展示。
const fileInfo = computed<PatchFileInfo | null>(() => {
  if (!fileContent.value) return null
  const path = filePath.value || 'unknown'
  const fileLines = fileContent.value.split('\n')
  return {
    status: 'add',
    oldPath: path,
    newPath: path,
    additions: fileLines.length,
    deletions: 0,
    isBinary: false,
    lines: fileLines.map((line, index) => ({
      type: 'add' as const,
      oldLineNumber: null,
      newLineNumber: index + 1,
      displayLineNumber: index + 1,
      prefix: '+',
      content: line,
      raw: `+${line}`,
    })),
  }
})
</script>

<template>
  <!-- 展开或收起新建文件内容 -->
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
      <MkIcon name="icon_file-add_outlined" />
      <span class="min-w-0 max-w-[300px] truncate" :title="title">{{ title }}</span>
      <span v-if="fileInfo" class="shrink-0 font-mono" style="color: var(--el-color-success-dark-2)">+{{ fileInfo.additions }}</span>
    </template>

    <div>
      <ScrollDiff v-if="fileInfo" :file="fileInfo" />
      <div v-else-if="loading">
        <span class="mk-conversation-loading" />
      </div>
    </div>
  </MkCollapse>
</template>
