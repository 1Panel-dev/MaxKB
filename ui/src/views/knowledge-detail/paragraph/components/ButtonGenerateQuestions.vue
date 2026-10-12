<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import type ParagraphApi from '@/api/admin/workspace/knowledge/paragraph'
import type { RelatedQuestionsConfig } from '@/api/types'
import GenerateQuestionsDialog from '@/components/business/generate-questions/GenerateQuestionsDialog.vue'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'ButtonGenerateQuestions' })
const props = defineProps<{
  api: typeof ParagraphApi
  knowledgeId: string
  documentId: string
  paragraphIds: string[]
  disabled?: boolean
}>()
const emit = defineEmits<{ refresh: [] }>()

// 打开时固定本次生成问题的分段与所属文档。
const loading = ref(false)
const dialogMounted = ref(false)
const dialogRef = useTemplateRef<InstanceType<typeof GenerateQuestionsDialog>>('dialogRef')
const targetParagraphIds = ref<string[]>([])
const targetKnowledgeId = ref('')
const targetDocumentId = ref('')
const refreshOnClosed = ref(false)

function handleOpenDialog() {
  if (props.disabled || loading.value || dialogMounted.value || !props.paragraphIds.length) return
  targetParagraphIds.value = [...props.paragraphIds]
  targetKnowledgeId.value = props.knowledgeId
  targetDocumentId.value = props.documentId
  dialogMounted.value = true
  return nextTick(() => dialogRef.value?.open())
}

// 仅提交勾选的分段，生成配置及用户缓存由公共弹窗维护。
function handleSubmit(config: RelatedQuestionsConfig) {
  if (props.disabled || loading.value || !targetParagraphIds.value.length) return
  loading.value = true
  return props.api
    .putGenerateParagraphQuestions(targetKnowledgeId.value, targetDocumentId.value, {
      ...config,
      paragraph_id_list: [...targetParagraphIds.value],
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
  targetParagraphIds.value = []
  targetKnowledgeId.value = ''
  targetDocumentId.value = ''
  // 关闭动画结束后刷新，避免清空勾选时卸载尚未关闭的弹窗。
  if (refreshOnClosed.value) {
    refreshOnClosed.value = false
    emit('refresh')
  }
}
</script>

<template>
  <!-- 批量生成分段关联问题 -->
  <el-button type="primary" plain :disabled="disabled || loading || !paragraphIds.length" @click="handleOpenDialog">生成问题</el-button>
  <GenerateQuestionsDialog
    v-if="dialogMounted"
    ref="dialogRef"
    :loading="loading"
    :show-paragraph-scope="false"
    @submit="handleSubmit"
    @closed="handleClosed"
  />
</template>
