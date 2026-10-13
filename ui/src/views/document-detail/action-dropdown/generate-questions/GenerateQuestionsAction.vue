<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import type ParagraphApi from '@/api/admin/workspace/knowledge/paragraph'
import type { RelatedQuestionsConfig } from '@/api/types'
import GenerateQuestionsDialog from '@/components/business/generate-questions/GenerateQuestionsDialog.vue'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'GenerateQuestionsAction' })
const props = defineProps<{
  api: typeof ParagraphApi
  knowledgeId: string
  documentId: string
  paragraphId: string
  label: string
  disabled?: boolean
}>()
const emit = defineEmits<{ refresh: [] }>()

// 打开时固定本次生成问题的分段与所属文档。
const loading = ref(false)
const dialogMounted = ref(false)
const dialogRef = useTemplateRef<InstanceType<typeof GenerateQuestionsDialog>>('dialogRef')
const targetParagraphId = ref('')
const targetKnowledgeId = ref('')
const targetDocumentId = ref('')
const refreshOnClosed = ref(false)

function handleOpenDialog() {
  if (props.disabled || loading.value || dialogMounted.value || !props.paragraphId) return
  targetParagraphId.value = props.paragraphId
  targetKnowledgeId.value = props.knowledgeId
  targetDocumentId.value = props.documentId
  dialogMounted.value = true
  return nextTick(() => dialogRef.value?.open())
}

// 仅提交当前分段，生成配置及用户缓存由公共弹窗维护。
function handleSubmit(config: RelatedQuestionsConfig) {
  if (props.disabled || loading.value || !targetParagraphId.value) return
  loading.value = true
  return props.api
    .putGenerateParagraphQuestions(targetKnowledgeId.value, targetDocumentId.value, {
      ...config,
      paragraph_id_list: [targetParagraphId.value],
    })
    .then(() => {
      MsgSuccess('操作成功')
      refreshOnClosed.value = true
      dialogRef.value?.close()
    })
    .catch(() => {
      // 请求层统一提示错误，保留生成配置。
    })
    .finally(() => {
      loading.value = false
    })
}

function handleClosed() {
  dialogMounted.value = false
  targetParagraphId.value = ''
  targetKnowledgeId.value = ''
  targetDocumentId.value = ''
  // 关闭动画结束后刷新，避免列表重载时卸载尚未关闭的弹窗。
  if (refreshOnClosed.value) {
    refreshOnClosed.value = false
    emit('refresh')
  }
}
</script>

<template>
  <!-- 生成当前分段的问题 -->
  <MkDropdownItem :disabled="disabled || loading || !paragraphId" @click="handleOpenDialog">
    <template #icon><MkIcon name="icon_link-record_outlined" /></template>
    {{ label }}
  </MkDropdownItem>
  <GenerateQuestionsDialog
    v-if="dialogMounted"
    ref="dialogRef"
    :loading="loading"
    :show-paragraph-scope="false"
    @submit="handleSubmit"
    @closed="handleClosed"
  />
</template>
