<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import type ParagraphApi from '@/api/admin/workspace/knowledge/paragraph'
import ParagraphMigrateDialog from './ParagraphMigrateDialog.vue'

defineOptions({ name: 'MigrateParagraphAction' })
const props = defineProps<{
  api: typeof ParagraphApi
  knowledgeId: string
  documentId: string
  paragraphId: string
  disabled?: boolean
}>()
const emit = defineEmits<{ success: [paragraphIds: string[]] }>()
const dialogMounted = ref(false)
const targetKnowledgeId = ref('')
const targetDocumentId = ref('')
const dialogRef = useTemplateRef<InstanceType<typeof ParagraphMigrateDialog>>('dialogRef')

function handleOpenDialog() {
  if (props.disabled || dialogMounted.value || !props.paragraphId) return
  const targetParagraphIds = [props.paragraphId]
  targetKnowledgeId.value = props.knowledgeId
  targetDocumentId.value = props.documentId
  dialogMounted.value = true
  return nextTick(() => dialogRef.value?.open(targetParagraphIds))
}
</script>

<template>
  <!-- 迁移当前分段 -->
  <MkDropdownItem :disabled="disabled || !paragraphId" @click="handleOpenDialog">
    <template #icon><MkIcon name="icon_move2_outlined" /></template>

    迁移
  </MkDropdownItem>
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
