<script setup lang="ts">
import { ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Conversation } from '../../core/types'
import RenameDialog from './RenameDialog.vue'

defineOptions({ name: 'RenameConversation' })

defineProps<{ conversation: Conversation; applicationId?: string }>()
const emit = defineEmits<{ renamed: [title: string] }>()
const { t } = useI18n({ useScope: 'global' })
const renameDialogRendered = ref(false)
</script>

<template>
  <!-- 重命名历史对话 -->
  <MkDropdownItem @click="renameDialogRendered = true">
    <template #icon><MkIcon name="icon_edit_outlined" /></template>
    <span>{{ t('common.actions.rename') }}</span>
  </MkDropdownItem>
  <RenameDialog
    v-if="renameDialogRendered"
    :conversation="conversation"
    :application-id="applicationId"
    @renamed="emit('renamed', $event)"
    @closed="renameDialogRendered = false"
  />
</template>
