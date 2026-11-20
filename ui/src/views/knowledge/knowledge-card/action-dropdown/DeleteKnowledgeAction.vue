<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type SystemResourceKnowledgeApi from '@/api/admin/system/resource-management/knowledge/knowledge'
import type SystemSharedKnowledgeApi from '@/api/admin/system/shared-resources/knowledge/knowledge'
import type KnowledgeApi from '@/api/admin/workspace/knowledge/knowledge'
import type { KnowledgeItem } from '@/api/types'
import { MsgConfirm, MsgSuccess } from '@/utils/message'

defineOptions({ name: 'DeleteKnowledgeAction' })
const { t } = useI18n({ useScope: 'global' })

const props = defineProps<{
  api: typeof KnowledgeApi | typeof SystemResourceKnowledgeApi | typeof SystemSharedKnowledgeApi
  knowledge: KnowledgeItem
  label: string
}>()

const loading = defineModel<boolean>('loading', { default: false })

const emit = defineEmits<{ delete: [knowledgeId: string] }>()

function handleDeleteKnowledge() {
  return MsgConfirm(t('knowledge.delete.title', { name: props.knowledge.name }), t('common.dialogs.deleteWarning'))
    .then(() => {
      loading.value = true
      return props.api
        .deleteKnowledge(props.knowledge.id)
        .finally(() => {
          loading.value = false
        })
        .then(() => {
          emit('delete', props.knowledge.id)
          MsgSuccess(t('common.messages.deleteSuccess'))
        })
    })
    .catch(() => {})
}
</script>

<template>
  <MkDropdownItem @click="handleDeleteKnowledge">
    <template #icon><MkIcon name="icon_delete-trash_outlined" /></template>
    <span>{{ label }}</span>
  </MkDropdownItem>
</template>
