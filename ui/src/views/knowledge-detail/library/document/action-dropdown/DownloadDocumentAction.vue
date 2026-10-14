<script setup lang="ts">
import { MsgSuccess } from '@/utils/message'
import type { useKnowledgeDetailContext } from '@/views/knowledge-detail/context'
import type { DocumentItem } from '@/api/types'

defineOptions({ name: 'DownloadDocumentAction' })
const props = defineProps<{
  api: ReturnType<typeof useKnowledgeDetailContext>['resourceApi']['document']
  knowledgeId: string
  document: DocumentItem
}>()
const loading = defineModel<boolean>('loading', { default: false })

// 下载原始文件，不清空勾选或刷新列表。
function handleDownload() {
  if (loading.value) return
  loading.value = true
  return (
    props.api
      .downloadDocumentSource?.(props.knowledgeId, props.document)
      .then(() => {
        MsgSuccess('操作成功')
      })
      .catch(() => {}) ?? Promise.resolve()
  ).finally(() => {
    loading.value = false
  })
}
</script>

<template>
  <!-- 下载原文档 -->
  <MkAction label="下载原文档" icon="icon_download_outlined" :disabled="loading" @click="handleDownload" />
</template>
