<script setup lang="ts">
import { useTemplateRef } from 'vue'
import type ToolApi from '@/api/admin/workspace/tool/tool'
import type SystemResourceToolApi from '@/api/admin/system/resource-management/tool/tool'
import type SystemSharedToolApi from '@/api/admin/system/shared-resources/tool/tool'
import type { ToolItem } from '@/api/types'
import EditToolForm from '@/views/tool/tool-form/EditToolForm.vue'

defineOptions({ name: 'EditToolAction' })

const props = defineProps<{
  api: typeof ToolApi | typeof SystemSharedToolApi | typeof SystemResourceToolApi
  display?: 'menu' | 'button'
  label: string
  tool: ToolItem
}>()

const emit = defineEmits<{ update: [tool: ToolItem] }>()
const editToolFormRef = useTemplateRef<InstanceType<typeof EditToolForm>>('editToolFormRef')

function handleOpenToolForm() {
  return editToolFormRef.value?.open(props.tool)
}
</script>

<template>
  <!-- 编辑工具 -->
  <MkAction :display="display" :label="label" icon="icon_edit_outlined" @click="handleOpenToolForm" />
  <EditToolForm ref="editToolFormRef" :api="api" @update="emit('update', $event)" />
</template>
