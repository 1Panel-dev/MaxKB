<script setup lang="ts">
import { computed, nextTick, ref, useTemplateRef } from 'vue'
import { DOCUMENT_TASK_TYPE } from '@/api/enums'
import type { DocumentItem, DocumentTaskState, RelatedQuestionsConfig } from '@/api/types'
import type DocumentApi from '@/api/admin/workspace/knowledge/document'
import GenerateQuestionsDialog from '@/components/business/generate-questions/GenerateQuestionsDialog.vue'
import { MsgSuccess } from '@/utils/message'
import { isDocumentTaskRunning } from '../../status'

defineOptions({ name: 'GenerateQuestionsAction' })
const props = defineProps<{
  api: typeof DocumentApi
  knowledgeId: string
  document: DocumentItem
  display?: 'menu' | 'button'
  disabled?: boolean
}>()
const emit = defineEmits<{ refresh: [] }>()
const loading = defineModel<boolean>('loading', { default: false })

// 单个文档在排队或执行时展示取消入口，其余状态打开生成配置。
const running = computed(() => isDocumentTaskRunning(props.document, DOCUMENT_TASK_TYPE.GENERATE_PROBLEM))

/* 打开时固定本次生成的目标文档。 */
const dialogMounted = ref(false)
const dialogRef = useTemplateRef<InstanceType<typeof GenerateQuestionsDialog>>('dialogRef')
const targetDocumentId = ref('')
const targetKnowledgeId = ref('')

function handleOpenDialog() {
  if (props.disabled || loading.value || dialogMounted.value || !props.document.id) return
  targetDocumentId.value = props.document.id
  targetKnowledgeId.value = props.knowledgeId
  dialogMounted.value = true
  return nextTick(() => dialogRef.value?.open())
}

// 取消当前文档的生成问题任务。
function handleCancelQuestions() {
  if (props.disabled || loading.value) return
  loading.value = true
  return props.api
    .putCancelTask(props.knowledgeId, props.document.id, DOCUMENT_TASK_TYPE.GENERATE_PROBLEM)
    .then(() => {
      MsgSuccess('操作成功')
      emit('refresh')
    })
    .catch(() => {})
    .finally(() => {
      loading.value = false
    })
}

/* Action 负责提交和成功后的页面刷新，失败保留配置。 */
function handleSubmit(config: RelatedQuestionsConfig, stateList: DocumentTaskState[]) {
  if (props.disabled || loading.value) return
  loading.value = true
  return props.api
    .putGenerateDocumentQuestions(targetKnowledgeId.value, {
      ...config,
      document_id_list: [targetDocumentId.value],
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
  targetDocumentId.value = ''
  targetKnowledgeId.value = ''
}
</script>

<template>
  <!-- 单个文档生成或取消生成问题 -->
  <MkAction
    :display="display ?? 'menu'"
    :label="running ? '取消生成问题' : '生成问题'"
    :icon="running ? 'icon_close_outlined' : 'icon_link-record_outlined'"
    :disabled="disabled || loading"
    @click="running ? handleCancelQuestions() : handleOpenDialog()"
  />
  <GenerateQuestionsDialog v-if="dialogMounted" ref="dialogRef" :loading="loading" @submit="handleSubmit" @closed="handleClosed" />
</template>
