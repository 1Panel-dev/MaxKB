<script setup lang="ts">
import type ToolApi from '@/api/admin/workspace/tool/tool'
import type { ToolItem } from '@/api/types'
import { MsgConfirm, MsgSuccess } from '@/utils/message'

defineOptions({ name: 'DeleteToolAction' })

const props = defineProps<{ api: typeof ToolApi; label: string; tool: ToolItem }>()

const loading = defineModel<boolean>('loading', { default: false })

const emit = defineEmits<{ delete: [toolId: string] }>()

function handleDeleteTool() {
  return MsgConfirm(`确认删除工具：${props.tool.name}？`)
    .then(() => {
      loading.value = true
      return props.api
        .deleteTool(props.tool.id)
        .finally(() => (loading.value = false))
        .then(() => {
          emit('delete', props.tool.id)
          MsgSuccess('删除成功')
        })
    })
    .catch(() => {})
}
</script>

<template>
  <MkDropdownItem divided @click="handleDeleteTool">
    <template #icon><MkIcon name="icon_delete-trash_outlined" /></template>
    <span>{{ label }}</span>
  </MkDropdownItem>
</template>
