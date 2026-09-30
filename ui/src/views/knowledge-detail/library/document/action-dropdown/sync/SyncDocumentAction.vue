<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import type DocumentApi from '@/api/admin/workspace/knowledge/document'
import { KNOWLEDGE_TYPE_KEY } from '@/constants/knowledge'
import type { DocumentItem } from '@/api/types'
import { MsgConfirm, MsgSuccess } from '@/utils/message'

defineOptions({ name: 'SyncDocumentAction' })
const props = defineProps<{
  api: typeof DocumentApi
  label: string
  knowledgeId: string
  document: DocumentItem
}>()
const route = useRoute()
const knowledgeType = computed(() => route.params.type)
const loading = defineModel<boolean>('loading', { default: false })
const emit = defineEmits<{ refresh: [] }>()

// 单项 Web 同步校验来源地址，确认覆盖后按知识库类型调用同步接口。
function handleSync() {
  if (loading.value) return
  const document = props.document
  if (!document.id) return
  if (knowledgeType.value === KNOWLEDGE_TYPE_KEY.WEB && !document.meta?.source_url) {
    MsgConfirm('提示', '无法同步，请先去设置文档 URL 地址', {
      confirmButtonText: '确认',
      confirmButtonType: 'primary',
      type: 'warning',
    })

    return
  }
  const knowledgeId = props.knowledgeId
  const documentId = document.id
  const isLark = knowledgeType.value === KNOWLEDGE_TYPE_KEY.LARK
  return MsgConfirm(`是否同步：${document.name}?`, '文档内容无更新时跳过，有更新时会使用新内容更新旧分段内容。', {
    cancelButtonText: '取消',
    confirmButtonText: '同步',
    confirmButtonType: 'primary',
  })
    .then(() => {
      if (loading.value) return
      loading.value = true
      const request = isLark ? props.api.putLarkDocumentSync(knowledgeId, documentId) : props.api.putDocumentSync(knowledgeId, documentId)
      return request
        .then(() => {
          MsgSuccess('操作成功')
          emit('refresh')
        })
        .finally(() => {
          loading.value = false
        })
    })
    .catch(() => {})
}
</script>

<template>
  <!-- 同步单个文档 -->
  <MkAction :label="label" icon="icon_replace_outlined" :disabled="loading" @click="handleSync" />
</template>
