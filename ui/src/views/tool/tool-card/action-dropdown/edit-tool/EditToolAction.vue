<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import type ToolApi from '@/api/admin/workspace/tool/tool'
import type { ToolItem, ToolStoreItem, ToolStoreResponse } from '@/api/types'
import { TOOL_TYPE } from '@/api/enums'
import ToolFormDrawer from '@/views/tool/tool-form/tool-custom/ToolFormDrawer.vue'
import DataSourceFormDrawer from '@/views/tool/tool-form/DataSourceFormDrawer.vue'
import McpFormDrawer from '@/views/tool/tool-form/McpFormDrawer.vue'
import SkillToolFormDrawer from '@/views/tool/tool-form/SkillToolFormDrawer.vue'
import WorkflowFormDialog from '@/views/tool/tool-form/WorkflowFormDialog.vue'
import ToolStoreDetailDrawer from '@/views/tool/tool-store/ToolStoreDetailDrawer.vue'
import AddStoreToolDialog from '@/views/tool/tool-store/AddStoreToolDialog.vue'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'EditToolAction' })

const props = defineProps<{
  api: typeof ToolApi
  label: string
  storeTools: ToolStoreResponse['apps']
  tool: ToolItem
}>()

const emit = defineEmits<{
  update: [tool: ToolItem]
}>()

const formMounted = ref(false)
const addStoreToolDialogRef =
  useTemplateRef<InstanceType<typeof AddStoreToolDialog>>('addStoreToolDialogRef')
const toolStoreDetailDrawerRef = useTemplateRef<InstanceType<typeof ToolStoreDetailDrawer>>(
  'toolStoreDetailDrawerRef',
)
const toolFormDrawerRef = useTemplateRef<InstanceType<typeof ToolFormDrawer>>('toolFormDrawerRef')
const dataSourceFormDrawerRef =
  useTemplateRef<InstanceType<typeof DataSourceFormDrawer>>('dataSourceFormDrawerRef')
const mcpFormDrawerRef = useTemplateRef<InstanceType<typeof McpFormDrawer>>('mcpFormDrawerRef')
const skillToolFormDrawerRef =
  useTemplateRef<InstanceType<typeof SkillToolFormDrawer>>('skillToolFormDrawerRef')
const workflowFormDialogRef =
  useTemplateRef<InstanceType<typeof WorkflowFormDialog>>('workflowFormDialogRef')

function handleOpenStoreToolDialog(tool: ToolItem, isEdit?: boolean) {
  addStoreToolDialogRef.value?.open(
    {
      desc: tool.desc,
      icon: tool.icon,
      id: tool.id,
      name: tool.name,
      source: 'store',
      tool_type: tool.tool_type,
      version: tool.version,
    },
    isEdit,
  )
}

function handleEditStoreTool(tool: ToolStoreItem, name: string) {
  props.api.putTool(tool.id, { name }).then((updatedTool) => {
    MsgSuccess('保存成功')
    emit('update', updatedTool)
  })
}

function handleOpenToolForm() {
  // 模板转换而来的工具只允许修改名称。
  if (props.tool.template_id) {
    formMounted.value = true
    void nextTick(() => handleOpenStoreToolDialog(props.tool, true))
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
      [TOOL_TYPE.DATA_SOURCE]: dataSourceFormDrawerRef,
      [TOOL_TYPE.MCP]: mcpFormDrawerRef,
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
    <AddStoreToolDialog
      v-if="tool.template_id"
      ref="addStoreToolDialogRef"
      @closed="handleFormClosed"
      @submit="handleEditStoreTool"
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
      @update="emit('update', $event)"
    />
    <DataSourceFormDrawer
      v-else-if="tool.tool_type === TOOL_TYPE.DATA_SOURCE"
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
  </template>
</template>
