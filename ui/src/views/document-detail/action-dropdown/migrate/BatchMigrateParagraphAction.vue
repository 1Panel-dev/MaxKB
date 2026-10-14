<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import type { DocumentParagraphApi } from '@/views/document-detail/context'
import ParagraphMigrateDialog from './ParagraphMigrateDialog.vue'

defineOptions({ name: 'BatchMigrateParagraphAction' })
const props = defineProps<{
  api: DocumentParagraphApi
  knowledgeId: string
  documentId: string
  paragraphIds: string[]
  disabled?: boolean
}>()
const emit = defineEmits<{ success: [paragraphIds: string[]] }>()
const dialogMounted = ref(false)
const targetKnowledgeId = ref('')
const targetDocumentId = ref('')
const dialogRef = useTemplateRef<InstanceType<typeof ParagraphMigrateDialog>>('dialogRef')

function handleOpenDialog() {
  if (props.disabled || dialogMounted.value || !props.paragraphIds.length) return
  const targetParagraphIds = [...props.paragraphIds]
  targetKnowledgeId.value = props.knowledgeId
  targetDocumentId.value = props.documentId
  dialogMounted.value = true
  return nextTick(() => dialogRef.value?.open(targetParagraphIds))
}
</script>

<template>
  <!-- 批量迁移分段 -->
  <el-button type="primary" plain :disabled="disabled || !paragraphIds.length" @click="handleOpenDialog">迁移至</el-button>
  <ParagraphMigrateDialog
    v-if="dialogMounted"
    ref="dialogRef"
    :api="api"
    :knowledge-id="targetKnowledgeId"
    :document-id="targetDocumentId"
    @closed="dialogMounted = false"
    @success="(paragraphIds) => emit('success', paragraphIds)"
  />
</template>
