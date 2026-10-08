<script setup lang="ts">
import type KnowledgeApi from '@/api/admin/workspace/knowledge/knowledge'
import type { KnowledgeItem } from '@/api/types'
import { MsgSuccess } from '@/utils/message'
import type SystemResourceKnowledgeApi from '@/api/admin/system/resource-management/knowledge/knowledge'

defineOptions({ name: 'EmbeddingKnowledgeAction' })

const props = defineProps<{
  api: typeof KnowledgeApi | typeof SystemResourceKnowledgeApi
  display?: 'menu' | 'button'
  knowledge: KnowledgeItem
  label: string
}>()
const loading = defineModel<boolean>('loading', { default: false })

/* 知识库向量化 */
function handleEmbedding() {
  if (loading.value) return
  loading.value = true
  return props.api
    .putReEmbeddingKnowledge(props.knowledge.id)
    .then(() => {
      MsgSuccess('提交成功')
    })
    .finally(() => {
      loading.value = false
    })
}
</script>

<template>
  <!-- 执行向量化 -->
  <MkAction
    :display="display"
    :label="label"
    icon="icon_sheet-datareference_outlined"
    :disabled="loading"
    @click="handleEmbedding"
  />
</template>
