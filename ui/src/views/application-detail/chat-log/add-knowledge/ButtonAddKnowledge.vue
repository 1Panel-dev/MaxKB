<script setup lang="ts">
import { useTemplateRef } from 'vue'
import type ChatLogApi from '@/api/admin/workspace/application/chat-log'
import AddKnowledgeDialog from './AddKnowledgeDialog.vue'

defineOptions({ name: 'ButtonAddKnowledge' })
const props = defineProps<{
  api: typeof ChatLogApi
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
  <el-button type="primary" plain :disabled="disabled || !chatIds.length" @click="handleOpenDialog">添加到知识库</el-button>
  <AddKnowledgeDialog ref="dialogRef" :api="api" :application-id="applicationId" @refresh="emit('refresh')" />
</template>
