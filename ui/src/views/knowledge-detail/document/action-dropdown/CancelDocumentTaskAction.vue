<script setup lang="ts">
import { MsgSuccess } from '@/utils/message'
import type DocumentApi from '@/api/admin/workspace/knowledge/document'
import type { DocumentTaskType } from '@/api/types'

defineOptions({ name: 'CancelDocumentTaskAction' })
const props = defineProps<{
  api: typeof DocumentApi
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
  return props.api
    .putBatchCancelDocumentTask(props.knowledgeId, ids, props.taskType)
    .then(() => {
      MsgSuccess('操作成功')
      emit('refresh')
    })
    .catch(() => {})
    .finally(() => {
      loading.value = false
    })
}
</script>

<template>
  <!-- 取消文档任务 -->
  <MkAction
    :label="label"
    icon="icon_close_outlined"
    :display="display"
    :divided="divided"
    :disabled="loading || !documentIds.length"
    @click="handleCancelTask"
  />
</template>
