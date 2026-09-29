<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import type { DocumentTaskState, RelatedQuestionsConfig } from '@/api/types'
import type DocumentApi from '@/api/admin/workspace/knowledge/document'
import GenerateQuestionsDialog from '@/components/business/generate-questions/GenerateQuestionsDialog.vue'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'GenerateDocumentQuestionsAction' })
const props = defineProps<{
  api: typeof DocumentApi
  knowledgeId: string
  documentIds: string[]
  batch?: boolean
  display?: 'menu' | 'button'
  disabled?: boolean
}>()
const emit = defineEmits<{ refresh: [] }>()
const loading = defineModel<boolean>('loading', { default: false })

/* 打开时固定目标文档，单项与批量共用文档生成接口。 */
const dialogMounted = ref(false)
const dialogRef = useTemplateRef<InstanceType<typeof GenerateQuestionsDialog>>('dialogRef')
const targetDocumentIds = ref<string[]>([])
const targetKnowledgeId = ref('')

function handleOpenDialog() {
  if (props.disabled || loading.value || dialogMounted.value || !props.documentIds.length) return
  targetDocumentIds.value = [...props.documentIds]
  targetKnowledgeId.value = props.knowledgeId
  dialogMounted.value = true
  return nextTick(() => dialogRef.value?.open())
}

/* Action 负责提交和成功后的页面刷新，失败保留配置。 */
function handleSubmit(config: RelatedQuestionsConfig, stateList: DocumentTaskState[]) {
  if (props.disabled || loading.value) return
  loading.value = true
  return props.api
    .putGenerateDocumentQuestions(targetKnowledgeId.value, {
      ...config,
      document_id_list: targetDocumentIds.value,
      state_list: stateList,
    })
    .then(() => {
      MsgSuccess('任务已提交')
      dialogRef.value?.close()
      emit('refresh')
    })
    .catch(() => {})
    .finally(() => {
      loading.value = false
    })
}

function handleClosed() {
  dialogMounted.value = false
  targetDocumentIds.value = []
  targetKnowledgeId.value = ''
}
</script>

<template>
  <!-- 批量生成问题 -->
  <el-button v-if="batch" :disabled="disabled || loading || !documentIds.length" @click="handleOpenDialog">生成问题</el-button>
  <!-- 单个文档生成问题 -->
  <MkAction
    v-else
    :display="display ?? 'menu'"
    label="生成问题"
    icon="icon_new-chat_outlined"
    :disabled="disabled || loading || !documentIds.length"
    @click="handleOpenDialog"
  />
  <GenerateQuestionsDialog v-if="dialogMounted" ref="dialogRef" :loading="loading" @submit="handleSubmit" @closed="handleClosed" />
</template>
