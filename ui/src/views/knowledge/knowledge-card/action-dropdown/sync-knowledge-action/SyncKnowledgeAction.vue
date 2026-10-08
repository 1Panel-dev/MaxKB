<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import type KnowledgeApi from '@/api/admin/workspace/knowledge/knowledge'
import type SystemResourceKnowledgeApi from '@/api/admin/system/resource-management/knowledge/knowledge'
import type { KnowledgeItem } from '@/api/types'
import KnowledgeSyncDialog from './KnowledgeSyncDialog.vue'

defineOptions({ name: 'SyncKnowledgeAction' })
defineProps<{ api: typeof KnowledgeApi | typeof SystemResourceKnowledgeApi; knowledge: KnowledgeItem; label: string }>()
const loading = defineModel<boolean>('loading', { default: false })

/* 知识库同步弹窗按需挂载 */
const dialogMounted = ref(false)
const syncDialogRef = useTemplateRef<InstanceType<typeof KnowledgeSyncDialog>>('syncDialogRef')

function handleOpenSync() {
  if (loading.value) return
  dialogMounted.value = true
  return nextTick(() => syncDialogRef.value?.open())
}

function handleDialogClosed() {
  dialogMounted.value = false
}
</script>

<template>
  <!-- 同步知识库 -->
  <MkDropdownItem :disabled="loading" @click.stop="handleOpenSync">
    <template #icon><MkIcon name="icon_replace_outlined" /></template>
    <span>{{ label }}</span>
  </MkDropdownItem>
  <KnowledgeSyncDialog
    v-if="dialogMounted"
    ref="syncDialogRef"
    v-model:loading="loading"
    :api="api"
    :knowledge-id="knowledge.id"
    @closed="handleDialogClosed"
  />
</template>
