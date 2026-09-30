<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import type DocumentApi from '@/api/admin/workspace/knowledge/document'
import { KNOWLEDGE_TYPE_KEY } from '@/constants/knowledge'
import type { DocumentItem } from '@/api/types'
import { MsgConfirm, MsgInfo, MsgSuccess } from '@/utils/message'

defineOptions({ name: 'SyncDocumentAction' })
const props = defineProps<{
  api: typeof DocumentApi
  knowledgeId: string
  documents: DocumentItem[]
  batch?: boolean
}>()
const route = useRoute()
const knowledgeType = computed(() => route.params.type)
const loading = defineModel<boolean>('loading', { default: false })
const emit = defineEmits<{ refresh: [] }>()

// 单项 Web 同步校验来源地址，确认覆盖后按知识库类型调用同步接口。
function handleSync() {
  if (!props.documents.length || loading.value) return
  const document = props.batch ? undefined : props.documents[0]
  if (document && knowledgeType.value === KNOWLEDGE_TYPE_KEY.WEB && !document.meta?.source_url) {
    MsgInfo('文档没有来源地址，请先在设置中填写文档地址')
    return
  }
  const ids = props.documents.map(({ id }) => id)
  return MsgConfirm('同步文档', '同步后将覆盖现有文档内容，是否继续？', { confirmButtonText: '同步' })
    .then(() => {
      if (loading.value) return
      loading.value = true
      const request =
        knowledgeType.value === KNOWLEDGE_TYPE_KEY.LARK
          ? props.api.putSyncLarkDocuments(props.knowledgeId, ids)
          : props.api.putSyncDocuments(props.knowledgeId, ids)
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
  <!-- 同步单个或选中文档 -->
  <MkAction :label="batch ? '同步文档' : '同步'" icon="icon_refresh_outlined" @click="handleSync" />
</template>
