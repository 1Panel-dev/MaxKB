<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import type { DocumentItem } from '@/api/types'
import type { useKnowledgeDetailContext } from '@/views/knowledge-detail/context'
import { KNOWLEDGE_TYPE_KEY } from '@/constants/knowledge'
import { isWorkFlow } from '@/utils/common'
import { MsgConfirm, MsgSuccess } from '@/utils/message'

defineOptions({ name: 'SyncDocumentAction' })
const { t } = useI18n({ useScope: 'global' })
const props = defineProps<{
  api: ReturnType<typeof useKnowledgeDetailContext>['resourceApi']['document']
  label: string
  knowledgeId: string
  document: DocumentItem
}>()
const route = useRoute()
const knowledgeType = computed(() => route.params.type)
const loading = defineModel<boolean>('loading', { default: false })
const emit = defineEmits<{ refresh: [] }>()

// Web 来源同步校验地址；工作流文档由服务端沿原数据源分支处理。
function handleSync() {
  if (loading.value) return
  const document = props.document
  if (!document.id) return
  const isWorkflow = isWorkFlow(String(knowledgeType.value ?? ''))
  if ((knowledgeType.value === KNOWLEDGE_TYPE_KEY.WEB || isWorkflow) && !document.meta?.source_url) {
    MsgConfirm(t('common.dialogs.notice'), t('knowledge.document.sync.missingUrlMessage'), {
      confirmButtonText: t('common.actions.confirm'),
      confirmButtonType: 'primary',
      type: 'warning',
    })

    return
  }
  const knowledgeId = props.knowledgeId
  const documentId = document.id
  const isLark = knowledgeType.value === KNOWLEDGE_TYPE_KEY.LARK
  const message = isWorkflow ? t('knowledge.document.sync.workflowDescription') : t('knowledge.document.sync.description')
  return MsgConfirm(t('knowledge.document.sync.title', { name: document.name }), message, {
    cancelButtonText: t('common.actions.cancel'),
    confirmButtonText: t('knowledge.actions.sync'),
    confirmButtonType: 'primary',
  })
    .then(() => {
      if (loading.value) return
      loading.value = true
      const request = isLark ? props.api.putLarkDocumentSync?.(knowledgeId, documentId) : props.api.putDocumentSync?.(knowledgeId, documentId)
      return (
        request?.then(() => {
          MsgSuccess(isWorkflow ? t('knowledge.sync.taskSubmitted') : t('common.messages.operationSuccess'))
          emit('refresh')
        }) ?? Promise.resolve()
      ).finally(() => {
        loading.value = false
      })
    })
    .catch(() => {})
}
</script>

<template>
  <!-- 同步单个文档 -->
  <MkAction :label="label" icon="icon_replace_outlined" :disabled="loading" @click="handleSync" />
</template>
