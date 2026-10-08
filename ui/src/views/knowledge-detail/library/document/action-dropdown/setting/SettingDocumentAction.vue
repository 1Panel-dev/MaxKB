<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import type { DocumentItem, DocumentSettingPayload } from '@/api/types'
import type DocumentApi from '@/api/admin/workspace/knowledge/document'
import { MsgSuccess } from '@/utils/message'
import DocumentSettingDialog from './DocumentSettingDialog.vue'

defineOptions({ name: 'SettingDocumentAction' })
const props = defineProps<{
  api: typeof DocumentApi
  knowledgeId: string
  document: DocumentItem
  label: string
  icon?: string
  disabled?: boolean
}>()
const loading = defineModel<boolean>('loading', { default: false })
const emit = defineEmits<{ refresh: [] }>()

// 打开设置时固定操作对象，弹窗关闭后卸载。
const dialogMounted = ref(false)
const settingDialogRef = useTemplateRef<InstanceType<typeof DocumentSettingDialog>>('settingDialogRef')
const targetKnowledgeId = ref('')
const targetDocumentId = ref('')

function handleOpenDialog() {
  if (props.disabled || loading.value || dialogMounted.value) return
  targetKnowledgeId.value = props.knowledgeId
  targetDocumentId.value = props.document.id
  const document = props.document
  dialogMounted.value = true
  return nextTick(() => settingDialogRef.value?.open(document))
}

// 设置成功后关闭弹窗并刷新列表，失败保留表单。
function handleSubmit(data: DocumentSettingPayload) {
  if (loading.value) return
  loading.value = true
  return props.api
    .putDocument(targetKnowledgeId.value, targetDocumentId.value, data)
    .then(() => {
      MsgSuccess('设置成功')
      settingDialogRef.value?.close()
      emit('refresh')
    })
    .catch(() => {
      // 请求层统一提示错误，保留当前输入。
    })
    .finally(() => {
      loading.value = false
    })
}

function handleDialogClosed() {
  dialogMounted.value = false
}
</script>

<template>
  <!-- 文档设置入口 -->
  <MkAction :label="label" :icon="icon" :disabled="disabled || loading" @click="handleOpenDialog" />
  <DocumentSettingDialog v-if="dialogMounted" ref="settingDialogRef" :loading="loading" @submit="handleSubmit" @closed="handleDialogClosed" />
</template>
