<script setup lang="ts">
import { DOCUMENT_TASK_STATE } from '@/api/enums'
import type DocumentApi from '@/api/admin/workspace/knowledge/document'

defineOptions({ name: 'BatchTokenizeAction' })
const props = defineProps<{ api: typeof DocumentApi; knowledgeId: string; documentIds: string[] }>()
const loading = defineModel<boolean>('loading', { default: false })
const emit = defineEmits<{ refresh: [] }>()

// 批量分词索引覆盖所选文档的全部分段状态。
function handleTokenize() {
  const documentIds = [...props.documentIds]
  if (!documentIds.length || loading.value) return
  loading.value = true
  return props.api
    .putBatchTokenizeDocuments(props.knowledgeId, documentIds, Object.values(DOCUMENT_TASK_STATE))
    .then(() => {
      emit('refresh')
    })
    .catch(() => {})
    .finally(() => {
      loading.value = false
    })
}
</script>

<template>
  <!-- 批量分词索引 -->
  <el-button plain :disabled="loading" @click="handleTokenize">分词索引</el-button>
</template>
