<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import type ToolApi from '@/api/admin/workspace/tool/tool'
import type { ToolItem, ToolStoreResponse } from '@/api/types'
import { TOOL_TYPE } from '@/api/enums'
import ToolFormDrawer from '@/views/tool/tool-form/tool-custom/ToolFormDrawer.vue'
import DataSourceFormDrawer from '@/views/tool/tool-form/DataSourceFormDrawer.vue'
import McpFormDrawer from '@/views/tool/tool-form/McpFormDrawer.vue'
import SkillToolFormDrawer from '@/views/tool/tool-form/SkillToolFormDrawer.vue'
import WorkflowFormDialog from '@/views/tool/tool-form/WorkflowFormDialog.vue'

defineOptions({ name: 'EditToolAction' })

const props = defineProps<{ api: typeof ToolApi; label: string; storeTools: ToolStoreResponse['apps']; tool: ToolItem }>()

const emit = defineEmits<{ update: [tool: ToolItem] }>()

const formMounted = ref(false)
const toolFormDrawerRef = useTemplateRef<InstanceType<typeof ToolFormDrawer>>('toolFormDrawerRef')
const dataSourceFormDrawerRef = useTemplateRef<InstanceType<typeof DataSourceFormDrawer>>('dataSourceFormDrawerRef')
const mcpFormDrawerRef = useTemplateRef<InstanceType<typeof McpFormDrawer>>('mcpFormDrawerRef')
const skillToolFormDrawerRef = useTemplateRef<InstanceType<typeof SkillToolFormDrawer>>('skillToolFormDrawerRef')
const workflowFormDialogRef = useTemplateRef<InstanceType<typeof WorkflowFormDialog>>('workflowFormDialogRef')

function handleOpenToolForm() {
  formMounted.value = true
  return nextTick(() => {
    if (props.tool.tool_type === TOOL_TYPE.DATA_SOURCE) {
      dataSourceFormDrawerRef.value?.open(props.tool)
    } else if (props.tool.tool_type === TOOL_TYPE.MCP) {
      mcpFormDrawerRef.value?.open(props.tool)
    } else if (props.tool.tool_type === TOOL_TYPE.SKILL) {
      skillToolFormDrawerRef.value?.open(props.tool)
    } else if (props.tool.tool_type === TOOL_TYPE.WORKFLOW) {
      workflowFormDialogRef.value?.open(props.tool)
    } else {
      toolFormDrawerRef.value?.open(props.tool)
    }
  })
}

function handleFormClosed() {
  formMounted.value = false
}
</script>

<template>
  <MkDropdownItem @click="handleOpenToolForm">
    <template #icon><MkIcon name="icon_edit_outlined" /></template>
    <span>{{ label }}</span>
  </MkDropdownItem>

  <template v-if="formMounted">
    <DataSourceFormDrawer
      v-if="tool.tool_type === TOOL_TYPE.DATA_SOURCE"
      ref="dataSourceFormDrawerRef"
      title="编辑数据源"
      :api="api"
      :folder-id="tool.folder_id ?? ''"
      @closed="handleFormClosed"
      @update="emit('update', $event)"
    />
    <McpFormDrawer
      v-else-if="tool.tool_type === TOOL_TYPE.MCP"
      ref="mcpFormDrawerRef"
      title="编辑 MCP"
      :api="api"
      :folder-id="tool.folder_id ?? ''"
      @closed="handleFormClosed"
      @update="emit('update', $event)"
    />
    <SkillToolFormDrawer
      v-else-if="tool.tool_type === TOOL_TYPE.SKILL"
      ref="skillToolFormDrawerRef"
      title="编辑 Skill"
      :api="api"
      :folder-id="tool.folder_id ?? ''"
      @closed="handleFormClosed"
      @update="emit('update', $event)"
    />
    <WorkflowFormDialog
      v-else-if="tool.tool_type === TOOL_TYPE.WORKFLOW"
      ref="workflowFormDialogRef"
      title="编辑工作流"
      :api="api"
      :folder-id="tool.folder_id ?? ''"
      @closed="handleFormClosed"
      @update="emit('update', $event)"
    />
    <ToolFormDrawer
      v-else
      ref="toolFormDrawerRef"
      title="编辑工具"
      :api="api"
      :folder-id="tool.folder_id ?? ''"
      @closed="handleFormClosed"
      @update="emit('update', $event)"
    />
  </template>
</template>
