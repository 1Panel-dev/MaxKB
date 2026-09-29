<script setup lang="ts">
import { MsgSuccess } from '@/utils/message'
import type DocumentApi from '@/api/admin/workspace/knowledge/document'
import { computed } from 'vue'
import { DOCUMENT_TASK_STATE, DOCUMENT_TASK_TYPE } from '@/api/enums'
import type { DocumentItem } from '@/api/types'
import { isDocumentTaskRunning } from '../utils'

defineOptions({ name: 'TokenizeDocumentAction' })
const props = defineProps<{ api: typeof DocumentApi; knowledgeId: string; documentIds: string[]; document?: DocumentItem; batch?: boolean }>()
const loading = defineModel<boolean>('loading', { default: false })
const emit = defineEmits<{ refresh: [] }>()

// 行操作根据任务状态切换为取消；批量操作始终提交分词索引。
const running = computed(() => isDocumentTaskRunning(props.document, DOCUMENT_TASK_TYPE.TOKENIZE))
function handleTokenize() {
  const ids = [...props.documentIds]
  if (!ids.length || loading.value) return
  loading.value = true
  const request = running.value
    ? props.api.putBatchCancelDocumentTask(props.knowledgeId, ids, DOCUMENT_TASK_TYPE.TOKENIZE)
    : props.api.putBatchTokenizeDocuments(props.knowledgeId, ids, Object.values(DOCUMENT_TASK_STATE))
  return request
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
  <!-- 批量分词索引 -->
  <el-button v-if="batch" :disabled="loading || !documentIds.length" @click="handleTokenize">分词索引</el-button>
  <!-- 分词索引或取消分词索引 -->
  <MkAction
    v-else
    display="button"
    :label="running ? '取消分词索引' : '分词索引'"
    :icon="running ? 'icon_close_outlined' : 'icon_add-dictionary_outlined'"
    :disabled="loading"
    @click="handleTokenize"
  />
</template>
