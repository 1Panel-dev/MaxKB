<script setup lang="ts">
import type DocumentApi from '@/api/admin/workspace/knowledge/document'
import type { DocumentItem } from '@/api/types'
import { MsgConfirm, MsgSuccess } from '@/utils/message'

defineOptions({ name: 'DeleteDocumentAction' })
const props = defineProps<{
  api: typeof DocumentApi
  knowledgeId: string
  document?: DocumentItem
  documentIds?: string[]
  batch?: boolean
}>()
const loading = defineModel<boolean>('loading', { default: false })
const emit = defineEmits<{ refresh: [] }>()

// 确认后删除单个或选中文档；刷新后的分页总数以服务端为准。
function handleDelete() {
  const { batch, document, knowledgeId } = props
  const ids = [...(props.documentIds ?? [])]
  // 批量确认展示数量，单个确认展示文档名称；确认期间保留本次删除目标。
  const confirmation = batch
    ? MsgConfirm(`是否删除选中的 ${ids.length} 个文档？`, '所选文档中的分段会跟随删除，请谨慎操作。')
    : MsgConfirm(`确认删除文档：${document!.name}？`, `此文档下的 ${document!.paragraph_count} 个分段都会被删除，请谨慎操作。`)
  return confirmation
    .then(() => {
      loading.value = true
      const request = batch ? props.api.putBatchDeleteDocuments(knowledgeId, ids) : props.api.deleteDocument(knowledgeId, document!.id)
      return request
        .then(() => {
          MsgSuccess('删除成功')
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
  <MkAction label="删除" @click="handleDelete" />
</template>
