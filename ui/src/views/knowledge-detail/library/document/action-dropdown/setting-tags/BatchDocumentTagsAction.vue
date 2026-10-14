<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import type DocumentApi from '@/api/admin/workspace/knowledge/document'
import AddTagDialog from './AddTagDialog.vue'

defineOptions({ name: 'BatchDocumentTagsAction' })
const props = defineProps<{
  api: typeof DocumentApi
  knowledgeId: string
  documentIds: string[]
  label: string
  disabled?: boolean
}>()
const loading = defineModel<boolean>('loading', { default: false })
const emit = defineEmits<{ refresh: [] }>()

const dialogMounted = ref(false)
const addTagRef = useTemplateRef<InstanceType<typeof AddTagDialog>>('addTagRef')
const targetKnowledgeId = ref('')

function handleOpenDialog() {
  if (props.disabled || loading.value || dialogMounted.value) return
  targetKnowledgeId.value = props.knowledgeId
  const documentIds = [...props.documentIds]
  dialogMounted.value = true
  return nextTick(() => addTagRef.value?.open(documentIds))
}

function handleDialogClosed() {
  dialogMounted.value = false
}
</script>

<template>
  <!-- 为选中文档批量添加标签 -->
  <el-button plain type="primary" :disabled="disabled || loading" @click="handleOpenDialog">{{ label }}</el-button>
  <AddTagDialog
    v-if="dialogMounted"
    ref="addTagRef"
    v-model:loading="loading"
    :api="api"
    :knowledge-id="targetKnowledgeId"
    @refresh="emit('refresh')"
    @closed="handleDialogClosed"
  />
</template>
