<script setup lang="ts">
import { useTemplateRef } from 'vue'
import type ParagraphApi from '@/api/admin/workspace/knowledge/paragraph'
import ParagraphMigrateDialog from './ParagraphMigrateDialog.vue'

defineOptions({ name: 'ButtonMigrateParagraph' })
const props = defineProps<{
  api: typeof ParagraphApi
  knowledgeId: string
  documentId: string
  paragraphIds: string[]
  disabled?: boolean
}>()
const emit = defineEmits<{ success: [paragraphIds: string[]] }>()
const dialogRef = useTemplateRef<InstanceType<typeof ParagraphMigrateDialog>>('dialogRef')

function handleOpenDialog() {
  if (props.disabled || !props.paragraphIds.length) return
  dialogRef.value?.open(props.paragraphIds)
}
</script>

<template>
  <!-- 批量迁移分段 -->
  <el-button type="primary" plain :disabled="disabled || !paragraphIds.length" @click="handleOpenDialog">迁移至</el-button>
  <ParagraphMigrateDialog
    ref="dialogRef"
    :api="api"
    :knowledge-id="knowledgeId"
    :document-id="documentId"
    @success="(paragraphIds) => emit('success', paragraphIds)"
  />
</template>
