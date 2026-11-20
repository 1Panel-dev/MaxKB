<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { DocumentItem, DocumentResourceType } from '@/api/types'
import type { useKnowledgeDetailContext } from '@/views/knowledge-detail/context'
import { DOCUMENT_RESOURCE_TYPE } from '@/api/enums'
import { MsgConfirm, MsgSuccess } from '@/utils/message'

defineOptions({ name: 'DeleteDocumentAction' })
const { t } = useI18n({ useScope: 'global' })
const props = withDefaults(
  defineProps<{
    api: ReturnType<typeof useKnowledgeDetailContext>['resourceApi']['document']
    knowledgeId: string
    document?: DocumentItem
    documentIds?: string[]
    batch?: boolean
    resourceType?: DocumentResourceType
  }>(),
  { resourceType: DOCUMENT_RESOURCE_TYPE.DOCUMENT },
)
const loading = defineModel<boolean>('loading', { default: false })
const emit = defineEmits<{ refresh: [] }>()

// 确定后删除单个或选中文档；刷新后的分页总数以服务端为准。
function handleDelete() {
  const { batch, document, knowledgeId, resourceType } = props
  const ids = [...(props.documentIds ?? [])]
  // 批量展示数量，单个确定展示文档名称；确认期间保留本次删除目标。
  const confirmation = batch
    ? MsgConfirm(
        t(
          resourceType === DOCUMENT_RESOURCE_TYPE.IMAGE ? 'knowledge.image.delete.batchTitle' : 'knowledge.document.delete.batchTitle',
          { count: ids.length },
          ids.length,
        ),
        t(resourceType === DOCUMENT_RESOURCE_TYPE.IMAGE ? 'knowledge.image.delete.batchDescription' : 'knowledge.document.delete.batchDescription'),
      )
    : MsgConfirm(
        t(resourceType === DOCUMENT_RESOURCE_TYPE.IMAGE ? 'knowledge.image.delete.title' : 'knowledge.document.delete.title', {
          name: document!.name,
        }),
        t(
          resourceType === DOCUMENT_RESOURCE_TYPE.IMAGE ? 'knowledge.image.delete.description' : 'knowledge.document.delete.description',
          document!.paragraph_count,
        ),
      )
  return confirmation
    .then(() => {
      loading.value = true
      const request = batch
        ? props.api.putBatchDeleteDocuments?.(knowledgeId, ids, resourceType)
        : props.api.deleteDocument?.(knowledgeId, document!.id)
      return (
        request?.then(() => {
          MsgSuccess(t('common.messages.deleteSuccess'))
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
  <!-- 删除单个或选中文档 -->
  <MkAction :label="t('common.actions.delete')" @click="handleDelete" />
</template>
