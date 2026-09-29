<script setup lang="ts">
import { computed, ref } from 'vue'
import { DOCUMENT_TASK_TYPE } from '@/api/enums'
import type { DocumentItem, DocumentTaskState } from '@/api/types'
import type DocumentApi from '@/api/admin/workspace/knowledge/document'
import { MsgSuccess } from '@/utils/message'
import DocumentEmbeddingDialog from './DocumentEmbeddingDialog.vue'
import { isDocumentTaskRunning } from '../../status'

defineOptions({ name: 'EmbeddingDocumentAction' })
const props = defineProps<{ api: typeof DocumentApi; knowledgeId: string; document: DocumentItem }>()
const loading = defineModel<boolean>('loading', { default: false })
const emit = defineEmits<{ refresh: [] }>()
const visible = ref(false)
const targetDocumentId = ref('')
const targetKnowledgeId = ref('')

// 单个文档在排队或执行时展示取消入口，其余状态打开向量化配置。
const running = computed(() => isDocumentTaskRunning(props.document, DOCUMENT_TASK_TYPE.EMBEDDING))

function handleOpenDialog() {
  if (loading.value) return
  targetDocumentId.value = props.document.id
  targetKnowledgeId.value = props.knowledgeId
  visible.value = true
}

// 取消当前文档的向量化任务。
function handleCancelEmbedding() {
  if (loading.value) return
  loading.value = true
  return props.api
    .putCancelTask(props.knowledgeId, props.document.id, DOCUMENT_TASK_TYPE.EMBEDDING)
    .then(() => {
      MsgSuccess('发送成功')
      emit('refresh')
    })
    .catch(() => {})
    .finally(() => {
      loading.value = false
    })
}

// 使用打开弹窗时的文档提交单项接口，失败保留弹窗和分段选择。
function handleEmbedding(stateList: DocumentTaskState[]) {
  loading.value = true
  return props.api
    .putDocumentRefresh(targetKnowledgeId.value, targetDocumentId.value, stateList)
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
  <!-- 向量化或取消向量化 -->
  <MkAction
    display="button"
    :label="running ? '取消向量化' : '向量化'"
    :icon="running ? 'icon_close_outlined' : 'icon_sheet-datareference_outlined'"
    :disabled="loading"
    @click="running ? handleCancelEmbedding() : handleOpenDialog()"
  />
  <DocumentEmbeddingDialog v-model="visible" :loading="loading" @submit="handleEmbedding" />
</template>
