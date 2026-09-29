<script setup lang="ts">
import type DocumentApi from '@/api/admin/workspace/knowledge/document'
import { MsgConfirm, MsgSuccess } from '@/utils/message'

defineOptions({ name: 'DeleteDocumentAction' })
const props = defineProps<{ api: typeof DocumentApi; knowledgeId: string; documentIds: string[]; batch?: boolean }>()
const loading = defineModel<boolean>('loading', { default: false })
const emit = defineEmits<{ refresh: [] }>()

// 确认后删除单个或选中文档；刷新后的分页总数以服务端为准。
function handleDelete() {
  if (!props.documentIds.length || loading.value) return
  const ids = [...props.documentIds]
  const documentId = ids[0]!
  return MsgConfirm(`删除 ${ids.length} 个文档`, '删除后无法恢复，是否继续？')
    .then(() => {
      if (loading.value) return
      loading.value = true
      const request = props.batch
        ? props.api.putBatchDeleteDocuments(props.knowledgeId, ids)
        : props.api.deleteDocument(props.knowledgeId, documentId)
      return request
        .then(() => {
          MsgSuccess('操作成功')
          emit('refresh')
        })
        .finally(() => {
          loading.value = false
        })
    })
    .catch(() => {})
}
</script>

<template>
  <!-- 删除单个或选中文档 -->
  <MkAction label="删除" :disabled="loading || !documentIds.length" @click="handleDelete" />
</template>
