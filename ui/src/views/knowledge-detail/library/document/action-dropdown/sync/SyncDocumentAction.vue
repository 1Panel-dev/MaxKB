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

// Web 来源同步校验地址；工作流文档由服务端沿原数据源分支处理。
function handleSync() {
  if (loading.value) return
  const document = props.document
  if (!document.id) return
  const isWorkflow = knowledgeType.value === KNOWLEDGE_TYPE_KEY.WORKFLOW
  if ((knowledgeType.value === KNOWLEDGE_TYPE_KEY.WEB || isWorkflow) && !document.meta?.source_url) {
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
  const message = isWorkflow
    ? '将按知识库工作流的提取、分段配置同步当前 Web 文档，其他文档保持不变。'
    : '文档内容无更新时跳过，有更新时会使用新内容更新旧分段内容。'
  return MsgConfirm(`是否同步：${document.name}?`, message, {
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
          MsgSuccess(isWorkflow ? '同步任务发送成功' : '操作成功')
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
