<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import type DocumentApi from '@/api/admin/workspace/knowledge/document'
import { KNOWLEDGE_TYPE_KEY } from '@/constants/knowledge'
import { MsgConfirm, MsgSuccess } from '@/utils/message'

defineOptions({ name: 'BatchSyncDocumentAction' })
const props = defineProps<{
  api: typeof DocumentApi
  label: string
  knowledgeId: string
  documentIds: string[]
}>()
const route = useRoute()
const knowledgeType = computed(() => route.params.type)
const loading = defineModel<boolean>('loading', { default: false })
const emit = defineEmits<{ refresh: [] }>()

// 固定选中文档，确认覆盖后按知识库类型调用批量同步接口。
function handleSync() {
  const knowledgeId = props.knowledgeId
  const documentIds = [...props.documentIds]
  const isLark = knowledgeType.value === KNOWLEDGE_TYPE_KEY.LARK
  return MsgConfirm(`是否同步选中的 ${documentIds.length} 个文档?`, '文档内容无更新时跳过，有更新时会使用新内容更新旧分段内容。', {
    cancelButtonText: '取消',
    confirmButtonText: '同步',
    confirmButtonType: 'primary',
  })
    .then(() => {
      if (loading.value) return
      loading.value = true
      const request = isLark ? props.api.putMulLarkSyncDocument(knowledgeId, documentIds) : props.api.putMulSyncDocument(knowledgeId, documentIds)
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
  <!-- 批量同步选中文档 -->
  <MkAction :label="label" :disabled="loading" @click="handleSync" />
</template>
