<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useI18n } from 'vue-i18n'
import type { useKnowledgeDetailContext } from '@/views/knowledge-detail/context'
import { KNOWLEDGE_TYPE_KEY } from '@/constants/knowledge'
import { MsgConfirm, MsgSuccess } from '@/utils/message'

defineOptions({ name: 'BatchSyncDocumentAction' })
const { t } = useI18n({ useScope: 'global' })
const props = defineProps<{
  api: ReturnType<typeof useKnowledgeDetailContext>['resourceApi']['document']
  label: string
  knowledgeId: string
  documentIds: string[]
}>()
const route = useRoute()
const knowledgeType = computed(() => route.params.type)
const loading = defineModel<boolean>('loading', { default: false })
const emit = defineEmits<{ refresh: [] }>()

// 固定选中文档，确定覆盖后按知识库类型调用批量同步接口。
function handleSync() {
  const knowledgeId = props.knowledgeId
  const documentIds = [...props.documentIds]
  const isLark = knowledgeType.value === KNOWLEDGE_TYPE_KEY.LARK
  return MsgConfirm(
    t('knowledge.document.sync.batchTitle', { count: documentIds.length }, documentIds.length),
    t('knowledge.document.sync.description'),
    {
      cancelButtonText: t('common.actions.cancel'),
      confirmButtonText: t('knowledge.sync.label'),
      confirmButtonType: 'primary',
    },
  )
    .then(() => {
      if (loading.value) return
      loading.value = true
      const request = isLark ? props.api.putMulLarkSyncDocument?.(knowledgeId, documentIds) : props.api.putMulSyncDocument?.(knowledgeId, documentIds)
      return (
        request?.then(() => {
          MsgSuccess(t('common.messages.operationSuccess'))
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
  <!-- 批量同步选中文档 -->
  <MkAction :label="label" :disabled="loading" @click="handleSync" />
</template>
