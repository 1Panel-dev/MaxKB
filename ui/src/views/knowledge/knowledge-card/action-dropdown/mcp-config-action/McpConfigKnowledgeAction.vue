<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import type KnowledgeApi from '@/api/admin/workspace/knowledge/knowledge'
import type { KnowledgeItem } from '@/api/types'
import KnowledgeMcpConfigDialog from './KnowledgeMcpConfigDialog.vue'
import type SystemResourceKnowledgeApi from '@/api/admin/system/resource-management/knowledge/knowledge'

defineOptions({ name: 'McpConfigKnowledgeAction' })

const props = defineProps<{ api: typeof KnowledgeApi | typeof SystemResourceKnowledgeApi; knowledge: KnowledgeItem; label: string }>()
const loading = defineModel<boolean>('loading', { default: false })

/* 知识库 MCP 配置详情 */
const dialogMounted = ref(false)
const mcpConfigDialogRef = useTemplateRef<InstanceType<typeof KnowledgeMcpConfigDialog>>('mcpConfigDialogRef')

function handleOpenMcpConfig() {
  if (loading.value) return
  loading.value = true
  return props.api
    .getKnowledgeMcpConfig(props.knowledge.id)
    .then((config) => {
      dialogMounted.value = true
      return nextTick(() => mcpConfigDialogRef.value?.open(config))
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
  <!-- 查看 MCP 配置详情 -->
  <MkDropdownItem :disabled="loading" @click.stop="handleOpenMcpConfig">
    <template #icon><MkIcon name="icon_describe_outlined" /></template>
    <span>{{ label }}</span>
  </MkDropdownItem>

  <KnowledgeMcpConfigDialog v-if="dialogMounted" ref="mcpConfigDialogRef" @closed="handleDialogClosed" />
</template>
