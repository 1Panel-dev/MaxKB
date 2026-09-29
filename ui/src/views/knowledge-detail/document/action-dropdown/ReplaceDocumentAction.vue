<script setup lang="ts">
import { MsgSuccess } from '@/utils/message'
import type DocumentApi from '@/api/admin/workspace/knowledge/document'
import type { UploadFile } from 'element-plus'
import type { DocumentItem } from '@/api/types'

defineOptions({ name: 'ReplaceDocumentAction' })
const props = defineProps<{ api: typeof DocumentApi; knowledgeId: string; document: DocumentItem }>()
const loading = defineModel<boolean>('loading', { default: false })
const emit = defineEmits<{ refresh: [] }>()

// 上传本地文件替换原文档，成功后通知页面刷新。
function handleReplace(file: UploadFile) {
  if (!file.raw || loading.value) return
  loading.value = true
  return props.api
    .postReplaceDocumentSource(props.knowledgeId, props.document.id, file.raw)
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
  <!-- 替换原文档 -->
  <el-upload action="#" :auto-upload="false" :show-file-list="false" :file-list="[]" :disabled="loading" :on-change="handleReplace">
    <MkDropdownItem :disabled="loading">
      <template #icon><MkIcon name="icon_upload_outlined" /></template>
      替换原文档
    </MkDropdownItem>
  </el-upload>
</template>
