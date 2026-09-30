<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import type { DocumentSettingPayload } from '@/api/types'
import type DocumentApi from '@/api/admin/workspace/knowledge/document'
import { MsgSuccess } from '@/utils/message'
import DocumentSettingDialog from './DocumentSettingDialog.vue'

defineOptions({ name: 'BatchSettingDocumentAction' })
const props = defineProps<{ api: typeof DocumentApi; knowledgeId: string; documentIds: string[]; label: string; disabled?: boolean }>()
const loading = defineModel<boolean>('loading', { default: false })
const emit = defineEmits<{ refresh: [] }>()

// 打开设置时固定操作对象，弹窗关闭后卸载。
const dialogMounted = ref(false)
const settingDialogRef = useTemplateRef<InstanceType<typeof DocumentSettingDialog>>('settingDialogRef')
const targetKnowledgeId = ref('')
const targetDocumentIds = ref<string[]>([])

function handleOpenDialog() {
  if (props.disabled || loading.value || dialogMounted.value || !props.documentIds.length) return
  targetKnowledgeId.value = props.knowledgeId
  targetDocumentIds.value = [...props.documentIds]
  dialogMounted.value = true
  return nextTick(() => settingDialogRef.value?.open())
}

// 设置成功后关闭弹窗并刷新列表，失败保留表单。
function handleSubmit(data: DocumentSettingPayload) {
  if (loading.value) return
  loading.value = true
  return props.api
    .putBatchDocumentSetting(targetKnowledgeId.value, targetDocumentIds.value, data)
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
  <!-- 批量文档设置 -->
  <el-button plain :disabled="disabled || loading" @click="handleOpenDialog">{{ label }}</el-button>
  <DocumentSettingDialog v-if="dialogMounted" ref="settingDialogRef" batch :loading="loading" @submit="handleSubmit" @closed="handleDialogClosed" />
</template>
