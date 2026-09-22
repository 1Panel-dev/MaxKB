<script setup lang="ts">
import type ToolApi from '@/api/admin/workspace/tool/tool'
import type SystemResourceToolApi from '@/api/admin/system/resource-management/tool/tool'
import type SystemSharedToolApi from '@/api/admin/system/shared-resources/tool/tool'
import type { ExportError, ToolItem } from '@/api/types'
import { MsgError } from '@/utils/message'

defineOptions({ name: 'ExportToolAction' })

const props = defineProps<{ api: typeof ToolApi | typeof SystemSharedToolApi | typeof SystemResourceToolApi; label: string; tool: ToolItem }>()

const loading = defineModel<boolean>('loading', { default: false })

function handleExportTool() {
  loading.value = true
  return props.api
    .exportTool(props.tool.id, props.tool.name)
    .catch((error: ExportError) => {
      if (error.response.status !== 403) {
        return error.response.data.text().then((response: string) => {
          MsgError(`导出失败：${JSON.parse(response).message}`)
        })
      }
    })
    .finally(() => (loading.value = false))
}
</script>

<template>
  <!-- 导出工具 -->
  <MkAction :label="label" icon="icon_export_outlined" divided @click="handleExportTool" />
</template>
