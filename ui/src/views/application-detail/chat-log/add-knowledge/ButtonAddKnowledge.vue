<script setup lang="ts">
import { useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ApplicationChatLogApi } from '../../context'
import AddKnowledgeDialog from './AddKnowledgeDialog.vue'

defineOptions({ name: 'ButtonAddKnowledge' })
const { t } = useI18n({ useScope: 'global' })
const props = defineProps<{
  api: ApplicationChatLogApi
  applicationId: string
  chatIds: string[]
  disabled?: boolean
}>()
const emit = defineEmits<{ refresh: [] }>()
const dialogRef = useTemplateRef<InstanceType<typeof AddKnowledgeDialog>>('dialogRef')

function handleOpenDialog() {
  if (props.disabled || !props.chatIds.length) return
  dialogRef.value?.open(props.chatIds)
}
</script>

<template>
  <!-- 批量添加对话到知识库 -->
  <el-button type="primary" plain :disabled="disabled || !chatIds.length" @click="handleOpenDialog">
    {{ t('application.chatLog.addKnowledge.title') }}
  </el-button>
  <AddKnowledgeDialog ref="dialogRef" :api="api" :application-id="applicationId" @refresh="emit('refresh')" />
</template>
