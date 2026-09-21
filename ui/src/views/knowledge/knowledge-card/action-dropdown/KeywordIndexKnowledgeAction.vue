<script setup lang="ts">
import { Share } from '@element-plus/icons-vue'
import type KnowledgeApi from '@/api/admin/workspace/knowledge/knowledge'
import type { KnowledgeItem } from '@/api/types'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'KeywordIndexKnowledgeAction' })

const props = defineProps<{ api: typeof KnowledgeApi; knowledge: KnowledgeItem; label: string }>()
const loading = defineModel<boolean>('loading', { default: false })

/* 知识库分词索引 */
function handleKeywordIndex() {
  if (loading.value) return
  loading.value = true
  return props.api
    .postKnowledgeKeywordIndex(props.knowledge.id)
    .then(() => {
      MsgSuccess('操作成功')
    })
    .finally(() => {
      loading.value = false
    })
}
</script>

<template>
  <!-- 执行分词索引 -->
  <MkDropdownItem :disabled="loading" @click.stop="handleKeywordIndex">
    <template #icon><MkIcon :icon="Share" /></template>
    <span>{{ label }}</span>
  </MkDropdownItem>
</template>
