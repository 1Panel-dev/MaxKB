<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import type ApplicationApi from '@/api/admin/workspace/application/application'
import type { ApplicationDetail } from '@/api/types'
import { RESOURCE_TYPE } from '@/api/enums'
import { FOLDER_ENTRY_ID } from '@/constants'
import MoveToDialog from '@/components/business/folder-tree/MoveToDialog.vue'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'MoveApplicationAction' })

const props = defineProps<{ api: typeof ApplicationApi; application: ApplicationDetail; currentFolderId: string; label: string }>()

const loading = defineModel<boolean>('loading', { default: false })

const emit = defineEmits<{ delete: [applicationId: string] }>()

const dialogMounted = ref(false)
const moveToDialogRef = useTemplateRef<{ close: () => void; open: (currentFolderId?: string) => void }>('moveToDialogRef')

function handleOpenMoveApplication() {
  dialogMounted.value = true
  return nextTick(() => moveToDialogRef.value?.open(props.application.folder ?? props.currentFolderId))
}

function handleMoveApplication(targetFolderId: string) {
  if (loading.value) return
  loading.value = true
  return props.api
    .putMoveApplication(props.application.id, targetFolderId)
    .finally(() => {
      loading.value = false
    })
    .then(() => {
      MsgSuccess('移动成功')
      moveToDialogRef.value?.close()
      if (props.currentFolderId !== FOLDER_ENTRY_ID.ALL) emit('delete', props.application.id)
    })
}

function handleDialogClosed() {
  dialogMounted.value = false
}
</script>

<template>
  <MkDropdownItem @click="handleOpenMoveApplication">
    <template #icon><MkIcon name="icon_move2_outlined" /></template>
    <span>{{ label }}</span>
  </MkDropdownItem>

  <MoveToDialog
    v-if="dialogMounted"
    ref="moveToDialogRef"
    :loading="loading"
    :source="RESOURCE_TYPE.APPLICATION"
    @closed="handleDialogClosed"
    @submit="handleMoveApplication"
  />
</template>
