<script setup lang="ts">
import { MsgSuccess } from '@/utils/message'
import type DocumentApi from '@/api/admin/workspace/knowledge/document'

defineOptions({ name: 'ExportDocumentAction' })
const props = defineProps<{ api: typeof DocumentApi; knowledgeId: string; documentIds: string[]; format: 'excel' | 'zip' }>()
const loading = defineModel<boolean>('loading', { default: false })

// 导出单个或选中文档，保留列表和勾选状态。
function handleExport() {
  const ids = [...props.documentIds]
  if (!ids.length || loading.value) return
  loading.value = true
  return props.api
    .exportDocuments(props.knowledgeId, ids, props.format)
    .then(() => {
      MsgSuccess('操作成功')
    })
    .catch(() => {})
    .finally(() => {
      loading.value = false
    })
}
</script>

<template>
  <!-- 导出文档 -->
  <MkAction
    :label="format === 'excel' ? '导出 Excel' : '导出 Zip'"
    icon="icon_export_outlined"
    :disabled="loading || !documentIds.length"
    @click="handleExport"
  />
</template>
