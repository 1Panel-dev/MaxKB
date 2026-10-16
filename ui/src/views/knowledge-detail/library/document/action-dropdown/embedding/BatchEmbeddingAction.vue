<script setup lang="ts">
import { ref } from 'vue'
import type { useKnowledgeDetailContext } from '@/views/knowledge-detail/context'
import { DOCUMENT_RESOURCE_TYPE } from '@/api/enums'
import type { DocumentResourceType, DocumentTaskState } from '@/api/types'
import DocumentEmbeddingDialog from './DocumentEmbeddingDialog.vue'

defineOptions({ name: 'BatchEmbeddingAction' })
const props = withDefaults(
  defineProps<{
    api: ReturnType<typeof useKnowledgeDetailContext>['resourceApi']['document']
    knowledgeId: string
    documentIds: string[]
    resourceType?: DocumentResourceType
  }>(),
  { resourceType: DOCUMENT_RESOURCE_TYPE.DOCUMENT },
)
const loading = defineModel<boolean>('loading', { default: false })
const emit = defineEmits<{ refresh: [] }>()
const visible = ref(false)
const targetDocumentIds = ref<string[]>([])
const targetKnowledgeId = ref('')
const targetResourceType = ref<DocumentResourceType>(DOCUMENT_RESOURCE_TYPE.DOCUMENT)

// 打开时快照勾选项与资源类型，弹窗期间的选择变化不影响本次批量任务。
function handleOpen() {
  if (loading.value || !props.documentIds.length) return
  targetDocumentIds.value = [...props.documentIds]
  targetKnowledgeId.value = props.knowledgeId
  targetResourceType.value = props.resourceType
  visible.value = true
}

function handleSubmit(stateList: DocumentTaskState[]) {
  if (loading.value || !visible.value || !targetDocumentIds.value.length) return
  loading.value = true
  return (
    props.api
      .putBatchRefreshDocuments?.(targetKnowledgeId.value, targetDocumentIds.value, stateList, targetResourceType.value)
      .then(() => {
        visible.value = false
        emit('refresh')
      })
      .catch(() => {}) ?? Promise.resolve()
  ).finally(() => {
    loading.value = false
  })
}
</script>

<template>
  <!-- 批量向量化 -->
  <el-button plain type="primary" :disabled="loading" @click="handleOpen">向量化</el-button>
  <DocumentEmbeddingDialog v-model="visible" :loading="loading" @submit="handleSubmit" />
</template>
