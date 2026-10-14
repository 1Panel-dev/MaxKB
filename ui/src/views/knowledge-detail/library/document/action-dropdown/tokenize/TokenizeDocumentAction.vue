<script setup lang="ts">
import type { useKnowledgeDetailContext } from '@/views/knowledge-detail/context'
import { computed } from 'vue'
import { DOCUMENT_TASK_STATE, DOCUMENT_TASK_TYPE } from '@/api/enums'
import type { DocumentItem } from '@/api/types'
import { isDocumentTaskRunning } from '../../status'

defineOptions({ name: 'TokenizeDocumentAction' })
const props = defineProps<{
  api: ReturnType<typeof useKnowledgeDetailContext>['resourceApi']['document']
  knowledgeId: string
  document: DocumentItem
}>()
const loading = defineModel<boolean>('loading', { default: false })
const emit = defineEmits<{ refresh: [] }>()

// 单个文档在排队或执行时切换为取消分词索引。
const running = computed(() => isDocumentTaskRunning(props.document, DOCUMENT_TASK_TYPE.TOKENIZE))
function handleTokenize() {
  if (loading.value) return
  loading.value = true
  const request = running.value
    ? props.api.putCancelTask?.(props.knowledgeId, props.document.id, DOCUMENT_TASK_TYPE.TOKENIZE)
    : props.api.putDocumentTokenize?.(props.knowledgeId, props.document.id, Object.values(DOCUMENT_TASK_STATE))
  return (
    request
      ?.then(() => {
        emit('refresh')
      })
      .catch(() => {}) ?? Promise.resolve()
  ).finally(() => {
    loading.value = false
  })
}
</script>

<template>
  <!-- 分词索引或取消分词索引 -->
  <MkAction
    display="button"
    :label="running ? '取消分词索引' : '分词索引'"
    :icon="running ? 'icon_close_outlined' : 'icon_external_outlined'"
    :disabled="loading"
    @click="handleTokenize"
  />
</template>
