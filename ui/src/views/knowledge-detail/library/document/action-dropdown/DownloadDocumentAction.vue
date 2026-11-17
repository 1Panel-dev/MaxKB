<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { DocumentItem } from '@/api/types'
import type { useKnowledgeDetailContext } from '@/views/knowledge-detail/context'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'DownloadDocumentAction' })
const { t } = useI18n({ useScope: 'global' })
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
        MsgSuccess(t('common.messages.operationSuccess'))
      })
      .catch(() => {}) ?? Promise.resolve()
  ).finally(() => {
    loading.value = false
  })
}
</script>

<template>
  <!-- 下载原文档 -->
  <MkAction :label="t('knowledge.document.actions.downloadOriginal')" icon="icon_download_outlined" :disabled="loading" @click="handleDownload" />
</template>
