<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import type { DocumentItem } from '@/api/types'
import type { useKnowledgeDetailContext } from '@/views/knowledge-detail/context'
import type { UploadFile } from 'element-plus'
import { DOCUMENT_RESOURCE_TYPE } from '@/api/enums'
import { KNOWLEDGE_IMAGE_ACCEPT, KNOWLEDGE_IMAGE_EXTENSIONS } from '@/constants/knowledge'
import { MsgSuccess, MsgWarning } from '@/utils/message'

defineOptions({ name: 'ReplaceDocumentAction' })
const { t } = useI18n({ useScope: 'global' })
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
    const formats = KNOWLEDGE_IMAGE_EXTENSIONS.join('、')
    MsgWarning(t('knowledge.image.unsupportedFormatMessage', { formats }))
    return
  }
  loading.value = true
  return (
    props.api
      .postReplaceDocumentSource?.(props.knowledgeId, props.document.id, file.raw)
      .then(() => {
        MsgSuccess(t('common.messages.operationSuccess'))
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
      <span>{{ t('knowledge.document.actions.replaceOriginal') }}</span>
    </MkDropdownItem>
  </el-upload>
</template>
