<script setup lang="ts">
import { ref } from 'vue'
import type { Conversation } from '../../core/types'
import RenameDialog from './RenameDialog.vue'

defineOptions({ name: 'RenameConversation' })

defineProps<{ conversation: Conversation; applicationId?: string }>()
const emit = defineEmits<{ renamed: [title: string] }>()
const renameDialogRendered = ref(false)
</script>

<template>
  <!-- 重命名历史对话 -->
  <MkDropdownItem @click="renameDialogRendered = true">
    <template #icon><MkIcon name="icon_edit_outlined" /></template>
    <span>重命名</span>
  </MkDropdownItem>
  <RenameDialog
    v-if="renameDialogRendered"
    :conversation="conversation"
    :application-id="applicationId"
    @renamed="emit('renamed', $event)"
    @closed="renameDialogRendered = false"
  />
</template>
