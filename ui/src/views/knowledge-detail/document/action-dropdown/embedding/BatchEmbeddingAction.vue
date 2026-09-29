<script setup lang="ts">
import { ref } from 'vue'
import type DocumentApi from '@/api/admin/workspace/knowledge/document'
import type { DocumentTaskState } from '@/api/types'
import DocumentEmbeddingDialog from './DocumentEmbeddingDialog.vue'

defineOptions({ name: 'BatchEmbeddingAction' })
const props = defineProps<{ api: typeof DocumentApi; knowledgeId: string; documentIds: string[] }>()
const loading = defineModel<boolean>('loading', { default: false })
const emit = defineEmits<{ refresh: [] }>()
const visible = ref(false)
const targetDocumentIds = ref<string[]>([])
const targetKnowledgeId = ref('')

// 打开时快照勾选项，弹窗期间的选择变化不影响本次批量任务。
function handleOpen() {
  if (loading.value || !props.documentIds.length) return
  targetDocumentIds.value = [...props.documentIds]
  targetKnowledgeId.value = props.knowledgeId
  visible.value = true
}

function handleSubmit(stateList: DocumentTaskState[]) {
  if (loading.value || !visible.value || !targetDocumentIds.value.length) return
  loading.value = true
  return props.api
    .putBatchRefreshDocuments(targetKnowledgeId.value, targetDocumentIds.value, stateList)
    .then(() => {
      visible.value = false
      emit('refresh')
    })
    .catch(() => {})
    .finally(() => {
      loading.value = false
    })
}
</script>

<template>
  <!-- 批量向量化 -->
  <el-button plain :disabled="loading" @click="handleOpen">向量化</el-button>
  <DocumentEmbeddingDialog v-model="visible" :loading="loading" @submit="handleSubmit" />
</template>
