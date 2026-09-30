<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import type DocumentApi from '@/api/admin/workspace/knowledge/document'
import DocumentMigrateDialog from './DocumentMigrateDialog.vue'

defineOptions({ name: 'MigrateDocumentAction' })
const props = defineProps<{ api: typeof DocumentApi; knowledgeId: string; documentIds: string[]; label: string; icon?: string; disabled?: boolean }>()
const emit = defineEmits<{ refresh: [] }>()
const loading = ref(false)

// 迁移弹窗按需挂载，关闭动画结束后卸载。
const dialogMounted = ref(false)
const migrateDialogRef = useTemplateRef<InstanceType<typeof DocumentMigrateDialog>>('migrateDialogRef')

function handleOpenDialog() {
  const documentIds = [...props.documentIds]
  dialogMounted.value = true
  return nextTick(() => migrateDialogRef.value?.open(documentIds))
}

function handleDialogClosed() {
  dialogMounted.value = false
}
</script>

<template>
  <!-- 文档迁移入口 -->
  <MkAction :label="label" :icon="icon" :disabled="disabled || loading" @click="handleOpenDialog" />
  <DocumentMigrateDialog
    v-if="dialogMounted"
    ref="migrateDialogRef"
    v-model:loading="loading"
    :api="api"
    :knowledge-id="knowledgeId"
    @refresh="emit('refresh')"
    @closed="handleDialogClosed"
  />
</template>
