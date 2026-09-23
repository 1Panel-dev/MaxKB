<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import type ToolApi from '@/api/admin/workspace/tool/tool'
import type SystemResourceToolApi from '@/api/admin/system/resource-management/tool/tool'
import type SystemSharedToolApi from '@/api/admin/system/shared-resources/tool/tool'
import type { ToolItem } from '@/api/types'
import McpConfigDialog from './McpConfigDialog.vue'

defineOptions({ name: 'McpConfigAction' })

const props = defineProps<{ api: typeof ToolApi | typeof SystemSharedToolApi | typeof SystemResourceToolApi; label: string; tool: ToolItem }>()

const loading = defineModel<boolean>('loading', { default: false })

const dialogMounted = ref(false)
const mcpConfigDialogRef = useTemplateRef<InstanceType<typeof McpConfigDialog>>('mcpConfigDialogRef')

function handleOpenMcpConfig() {
  loading.value = true
  return props.api
    .getToolDetail(props.tool.id)
    .then((toolDetail) => {
      dialogMounted.value = true
      return nextTick(() => mcpConfigDialogRef.value?.open(toolDetail))
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
  <!-- 查看 MCP 配置 -->
  <MkDropdownItem @click="handleOpenMcpConfig">
    <template #icon><MkIcon name="icon_describe_outlined" /></template>
    <span>{{ label }}</span>
  </MkDropdownItem>

  <McpConfigDialog v-if="dialogMounted" ref="mcpConfigDialogRef" @closed="handleDialogClosed" />
</template>
