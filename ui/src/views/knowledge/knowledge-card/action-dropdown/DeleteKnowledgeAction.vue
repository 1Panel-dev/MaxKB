<script setup lang="ts">
import type KnowledgeApi from '@/api/admin/workspace/knowledge/knowledge'
import type { KnowledgeItem } from '@/api/types'
import { MsgConfirm, MsgSuccess } from '@/utils/message'

defineOptions({ name: 'DeleteKnowledgeAction' })

const props = defineProps<{ api: typeof KnowledgeApi; knowledge: KnowledgeItem; label: string }>()

const loading = defineModel<boolean>('loading', { default: false })

const emit = defineEmits<{ delete: [knowledgeId: string] }>()

function handleDeleteKnowledge() {
  return MsgConfirm(`确认删除知识库：${props.knowledge.name}？`, '删除后无法恢复，请谨慎操作。')
    .then(() => {
      loading.value = true
      return props.api
        .deleteKnowledge(props.knowledge.id)
        .finally(() => {
          loading.value = false
        })
        .then(() => {
          emit('delete', props.knowledge.id)
          MsgSuccess('删除成功')
        })
    })
    .catch(() => {})
}
</script>

<template>
  <MkDropdownItem divided @click="handleDeleteKnowledge">
    <template #icon><MkIcon name="icon_delete-trash_outlined" /></template>
    <span>{{ label }}</span>
  </MkDropdownItem>
</template>
