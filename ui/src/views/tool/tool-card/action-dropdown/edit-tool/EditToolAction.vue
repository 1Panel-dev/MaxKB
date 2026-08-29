<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import type ToolApi from '@/api/admin/workspace/tool/tool'
import type { ToolItem, ToolStoreItem, ToolStoreResponse } from '@/api/types'
import { TOOL_TYPE } from '@/api/enums'
import ToolFormDrawer from '@/views/tool/tool-form/tool-custom/ToolFormDrawer.vue'
import DataSourceToolFormDrawer from '@/views/tool/tool-form/tool-data-source/DataSourceToolFormDrawer.vue'
import McpToolFormDrawer from '@/views/tool/tool-form/tool-mcp/McpToolFormDrawer.vue'
import SkillToolFormDrawer from '@/views/tool/tool-form/tool-skills/SkillToolFormDrawer.vue'
import WorkflowFormDialog from '@/views/tool/tool-form/tool-workflow/WorkflowFormDialog.vue'
import ToolStoreDetailDrawer from '@/views/tool/tool-store/ToolStoreDetailDrawer.vue'
import AddInternalToolDialog from './AddInternalToolDialog.vue'

defineOptions({ name: 'EditToolAction' })

const props = defineProps<{
  api: typeof ToolApi
  label: string
  storeTools: ToolStoreResponse['apps']
  tool: ToolItem
}>()

const emit = defineEmits<{
  refresh: []
}>()

const formMounted = ref(false)
const addInternalToolDialogRef = useTemplateRef<InstanceType<typeof AddInternalToolDialog>>(
  'addInternalToolDialogRef',
)
const toolStoreDetailDrawerRef = useTemplateRef<InstanceType<typeof ToolStoreDetailDrawer>>(
  'toolStoreDetailDrawerRef',
)
const toolFormDrawerRef = useTemplateRef<InstanceType<typeof ToolFormDrawer>>('toolFormDrawerRef')
const dataSourceToolFormDrawerRef = useTemplateRef<InstanceType<typeof DataSourceToolFormDrawer>>(
  'dataSourceToolFormDrawerRef',
)
const mcpToolFormDrawerRef =
  useTemplateRef<InstanceType<typeof McpToolFormDrawer>>('mcpToolFormDrawerRef')
const skillToolFormDrawerRef =
  useTemplateRef<InstanceType<typeof SkillToolFormDrawer>>('skillToolFormDrawerRef')
const workflowFormDialogRef =
  useTemplateRef<InstanceType<typeof WorkflowFormDialog>>('workflowFormDialogRef')

function handleOpenToolForm() {
  // 模板转换而来的工具只允许修改名称。
  if (props.tool.template_id) {
    formMounted.value = true
    addInternalToolDialogRef.value?.open(props.tool)
    return
  }

  // 有版本号的展示readme，是商店更新过来的
  if (props.tool.version) {
    formMounted.value = true
    void nextTick(() => {
      const storeTool = props.storeTools.find((item) => item.id === props.tool.template_id)
      const toolDetail: ToolStoreItem = {
        ...storeTool,
        desc: props.tool.desc,
        icon: props.tool.icon,
        id: props.tool.id,
        name: props.tool.name,
        source: 'store',
        tool_type: props.tool.tool_type,
        version: props.tool.version,
      }
      toolStoreDetailDrawerRef.value?.open(toolDetail, storeTool?.readMe)
    })
    return
  }

  formMounted.value = true
  void nextTick(() => {
    const formRefMap = {
      [TOOL_TYPE.CUSTOM]: toolFormDrawerRef,
      [TOOL_TYPE.DATA_SOURCE]: dataSourceToolFormDrawerRef,
      [TOOL_TYPE.MCP]: mcpToolFormDrawerRef,
      [TOOL_TYPE.SKILL]: skillToolFormDrawerRef,
      [TOOL_TYPE.WORKFLOW]: workflowFormDialogRef,
    }
    formRefMap[props.tool.tool_type as keyof typeof formRefMap]?.value?.open(props.tool)
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
    <AddInternalToolDialog
      v-if="tool.template_id"
      ref="addInternalToolDialogRef"
      :api="api"
      @closed="handleFormClosed"
      @refresh="emit('refresh')"
    />
    <ToolStoreDetailDrawer
      v-else-if="tool.version"
      ref="toolStoreDetailDrawerRef"
      :show-add="false"
      @closed="handleFormClosed"
    />
    <ToolFormDrawer
      v-else-if="tool.tool_type === TOOL_TYPE.CUSTOM"
      ref="toolFormDrawerRef"
      title="编辑工具"
      :api="api"
      :folder-id="tool.folder_id ?? ''"
      @closed="handleFormClosed"
      @refresh="emit('refresh')"
    />
    <DataSourceToolFormDrawer
      v-else-if="tool.tool_type === TOOL_TYPE.DATA_SOURCE"
      ref="dataSourceToolFormDrawerRef"
      title="编辑数据源"
      :api="api"
      :folder-id="tool.folder_id ?? ''"
      @closed="handleFormClosed"
      @refresh="emit('refresh')"
    />
    <McpToolFormDrawer
      v-else-if="tool.tool_type === TOOL_TYPE.MCP"
      ref="mcpToolFormDrawerRef"
      title="编辑 MCP"
      :api="api"
      :folder-id="tool.folder_id ?? ''"
      @closed="handleFormClosed"
      @refresh="emit('refresh')"
    />
    <SkillToolFormDrawer
      v-else-if="tool.tool_type === TOOL_TYPE.SKILL"
      ref="skillToolFormDrawerRef"
      title="编辑 Skill"
      :api="api"
      :folder-id="tool.folder_id ?? ''"
      @closed="handleFormClosed"
      @refresh="emit('refresh')"
    />
    <WorkflowFormDialog
      v-else-if="tool.tool_type === TOOL_TYPE.WORKFLOW"
      ref="workflowFormDialogRef"
      title="编辑工作流"
      :api="api"
      :folder-id="tool.folder_id ?? ''"
      @closed="handleFormClosed"
      @refresh="emit('refresh')"
    />
  </template>
</template>
