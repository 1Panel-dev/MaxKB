<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import type { DocumentTaskState, RelatedQuestionsConfig } from '@/api/types'
import type DocumentApi from '@/api/admin/workspace/knowledge/document'
import GenerateQuestionsDialog from '@/components/business/generate-questions/GenerateQuestionsDialog.vue'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'BatchGenerateQuestionsAction' })
const props = defineProps<{
  api: typeof DocumentApi
  knowledgeId: string
  documentIds: string[]
  disabled?: boolean
}>()
const emit = defineEmits<{ refresh: [] }>()
const loading = defineModel<boolean>('loading', { default: false })

/* 打开时固定本次批量生成的目标文档。 */
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
      MsgSuccess('操作成功')
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
  <el-button plain :disabled="disabled || loading" @click="handleOpenDialog">生成问题</el-button>
  <GenerateQuestionsDialog v-if="dialogMounted" ref="dialogRef" :loading="loading" @submit="handleSubmit" @closed="handleClosed" />
</template>
