<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { DocumentTaskType } from '@/api/types'
import type { useKnowledgeDetailContext } from '@/views/knowledge-detail/context'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'BatchCancelTaskAction' })
const { t } = useI18n({ useScope: 'global' })
const props = defineProps<{
  api: ReturnType<typeof useKnowledgeDetailContext>['resourceApi']['document']
  knowledgeId: string
  documentIds: string[]
  taskType: DocumentTaskType
  label: string
  display?: 'menu' | 'button'
  divided?: boolean
}>()
const loading = defineModel<boolean>('loading', { default: false })
const emit = defineEmits<{ refresh: [] }>()

// 取消单个或选中文档的指定任务。
function handleCancelTask() {
  const ids = [...props.documentIds]
  if (!ids.length || loading.value) return
  loading.value = true
  return (
    props.api
      .putBatchCancelDocumentTask?.(props.knowledgeId, ids, props.taskType)
      .then(() => {
        MsgSuccess(t('common.messages.operationSuccess'))
        emit('refresh')
      })
      .catch(() => {}) ?? Promise.resolve()
  ).finally(() => {
    loading.value = false
  })
}
</script>

<template>
  <!-- 取消文档任务 -->
  <MkAction :label="label" :display="display" :divided="divided" :disabled="loading" @click="handleCancelTask" />
</template>
