<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import type KnowledgeApi from '@/api/admin/workspace/knowledge/knowledge'
import type { KnowledgeItem } from '@/api/types'
import { RESOURCE_TYPE } from '@/api/enums'
import { FOLDER_ENTRY_ID } from '@/constants'
import MoveToDialog from '@/components/business/folder-tree/MoveToDialog.vue'
import { KNOWLEDGE_TYPE_KEY, KNOWLEDGE_TYPE_MAP } from '@/constants/knowledge'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'MoveKnowledgeAction' })

const props = defineProps<{ api: typeof KnowledgeApi; knowledge: KnowledgeItem; currentFolderId: string; label: string }>()

const loading = defineModel<boolean>('loading', { default: false })

const emit = defineEmits<{ delete: [knowledgeId: string]; move: [knowledgeId: string, folderId: string] }>()

const dialogMounted = ref(false)
const moveToDialogRef = useTemplateRef<{ close: () => void; open: (currentFolderId?: string) => void }>('moveToDialogRef')

function handleOpenMoveKnowledge() {
  dialogMounted.value = true
  return nextTick(() => moveToDialogRef.value?.open(props.knowledge.folder_id ?? props.currentFolderId))
}

function handleMoveKnowledge(targetFolderId: string) {
  if (loading.value) return
  loading.value = true
  const updateKnowledge = KNOWLEDGE_TYPE_MAP[props.knowledge.type] === KNOWLEDGE_TYPE_KEY.LARK ? props.api.putLarkKnowledge : props.api.putKnowledge
  return updateKnowledge(props.knowledge.id, { folder_id: targetFolderId })
    .then(() => {
      MsgSuccess('转移成功')
      moveToDialogRef.value?.close()
      emit('move', props.knowledge.id, targetFolderId)
      if (props.currentFolderId !== FOLDER_ENTRY_ID.ALL && props.currentFolderId !== targetFolderId) emit('delete', props.knowledge.id)
    })
    .finally(() => {
      loading.value = false
    })
}

function handleDialogClosed() {
  dialogMounted.value = false
}
</script>

<template>
  <MkDropdownItem @click="handleOpenMoveKnowledge">
    <template #icon><MkIcon name="icon_move2_outlined" /></template>
    <span>{{ label }}</span>
  </MkDropdownItem>

  <MoveToDialog
    v-if="dialogMounted"
    ref="moveToDialogRef"
    :loading="loading"
    :source="RESOURCE_TYPE.KNOWLEDGE"
    @closed="handleDialogClosed"
    @submit="handleMoveKnowledge"
  />
</template>
