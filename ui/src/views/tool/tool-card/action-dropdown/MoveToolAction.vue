<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import type ToolApi from '@/api/admin/workspace/tool/tool'
import type { ToolItem } from '@/api/types'
import { RESOURCE_TYPE } from '@/api/enums'
import { FOLDER_ENTRY_ID } from '@/constants'
import MoveToDialog from '@/components/business/folder-tree/MoveToDialog.vue'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'MoveToolAction' })

const props = defineProps<{ api: typeof ToolApi; currentFolderId: string; label: string; tool: ToolItem }>()

const loading = defineModel<boolean>('loading', { default: false })

const emit = defineEmits<{ delete: [toolId: string] }>()

const dialogMounted = ref(false)
const moveToDialogRef = useTemplateRef<{ close: () => void; open: (currentFolderId?: string) => void }>('moveToDialogRef')

function handleOpenMoveTool() {
  dialogMounted.value = true
  return nextTick(() => moveToDialogRef.value?.open(props.tool.folder_id))
}

function handleMoveTool(targetFolderId: string) {
  if (loading.value) return
  loading.value = true
  return props.api
    .putTool(props.tool.id, { folder_id: targetFolderId })
    .finally(() => {
      loading.value = false
    })
    .then(() => {
      MsgSuccess('移动成功')
      moveToDialogRef.value?.close()
      if (props.currentFolderId !== FOLDER_ENTRY_ID.ALL) emit('delete', props.tool.id)
    })
}

function handleDialogClosed() {
  dialogMounted.value = false
}
</script>

<template>
  <MkDropdownItem @click="handleOpenMoveTool">
    <template #icon><MkIcon name="icon_move2_outlined" /></template>
    <span>{{ label }}</span>
  </MkDropdownItem>

  <MoveToDialog
    v-if="dialogMounted"
    ref="moveToDialogRef"
    :loading="loading"
    :source="RESOURCE_TYPE.TOOL"
    @closed="handleDialogClosed"
    @submit="handleMoveTool"
  />
</template>
