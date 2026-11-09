<script setup lang="ts">
import { computed } from 'vue'
import { MsgSuccess, MsgWarning } from '@/utils/message'
import { DOCUMENT_RESOURCE_TYPE } from '@/api/enums'
import { KNOWLEDGE_IMAGE_ACCEPT, KNOWLEDGE_IMAGE_EXTENSIONS, KNOWLEDGE_IMAGE_TYPE_LABEL } from '@/constants/knowledge'
import type { useKnowledgeDetailContext } from '@/views/knowledge-detail/context'
import type { UploadFile } from 'element-plus'
import type { DocumentItem } from '@/api/types'

defineOptions({ name: 'ReplaceDocumentAction' })
const props = defineProps<{
  api: ReturnType<typeof useKnowledgeDetailContext>['resourceApi']['document']
  knowledgeId: string
  document: DocumentItem
}>()
const loading = defineModel<boolean>('loading', { default: false })
const emit = defineEmits<{ refresh: [] }>()
const isImage = computed(() => props.document.resource_type === DOCUMENT_RESOURCE_TYPE.IMAGE)
const accept = computed(() => (isImage.value ? KNOWLEDGE_IMAGE_ACCEPT : ''))

// 上传本地文件替换原文档，成功后通知页面刷新。
function handleReplace(file: UploadFile) {
  if (!file.raw || loading.value) return
  if (isImage.value && !KNOWLEDGE_IMAGE_EXTENSIONS.includes(file.raw.name.split('.').pop()?.toUpperCase() ?? '')) {
    MsgWarning(`仅支持 ${KNOWLEDGE_IMAGE_TYPE_LABEL} 格式的图片`)
    return
  }
  loading.value = true
  return (
    props.api
      .postReplaceDocumentSource?.(props.knowledgeId, props.document.id, file.raw)
      .then(() => {
        MsgSuccess('操作成功')
        emit('refresh')
      })
      .catch(() => {}) ?? Promise.resolve()
  ).finally(() => {
    loading.value = false
  })
}
</script>

<template>
  <!-- 替换原文档 -->
  <el-upload action="#" :accept="accept" :auto-upload="false" :show-file-list="false" :file-list="[]" :disabled="loading" :on-change="handleReplace">
    <MkDropdownItem :disabled="loading">
      <template #icon><MkIcon name="icon_doc-replace_outlined" /></template>
      <span>替换原文档</span>
    </MkDropdownItem>
  </el-upload>
</template>
