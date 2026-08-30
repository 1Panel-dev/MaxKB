<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type ToolApi from '@/api/admin/workspace/tool/tool'
import type { ToolItem } from '@/api/types'
import { TOOL_TYPE } from '@/api/enums'
import ToolFormDrawer from '@/views/tool/tool-form/tool-custom/ToolFormDrawer.vue'
import DataSourceFormDrawer from '@/views/tool/tool-form/DataSourceFormDrawer.vue'
import McpFormDrawer from '@/views/tool/tool-form/McpFormDrawer.vue'
import SkillToolFormDrawer from '@/views/tool/tool-form/SkillToolFormDrawer.vue'
import WorkflowFormDialog from '@/views/tool/tool-form/WorkflowFormDialog.vue'

defineOptions({ name: 'CopyToolAction' })

const props = defineProps<{ api: typeof ToolApi; label: string; tool: ToolItem }>()

const loading = defineModel<boolean>('loading', { default: false })

const emit = defineEmits<{ refresh: [] }>()

const formMounted = ref(false)
const toolFormDrawerRef = useTemplateRef<InstanceType<typeof ToolFormDrawer>>('toolFormDrawerRef')
const dataSourceFormDrawerRef = useTemplateRef<InstanceType<typeof DataSourceFormDrawer>>('dataSourceFormDrawerRef')
const mcpFormDrawerRef = useTemplateRef<InstanceType<typeof McpFormDrawer>>('mcpFormDrawerRef')
const skillToolFormDrawerRef = useTemplateRef<InstanceType<typeof SkillToolFormDrawer>>('skillToolFormDrawerRef')
const workflowFormDialogRef = useTemplateRef<InstanceType<typeof WorkflowFormDialog>>('workflowFormDialogRef')

function handleCopyTool() {
  loading.value = true
  return props.api
    .getToolDetail(props.tool.id)
    .then((toolDetail) => {
      const copiedTool = cloneDeep(toolDetail)
      copiedTool.name = `${copiedTool.name}  副本`
      formMounted.value = true

      return nextTick(() => {
        if (copiedTool.tool_type === TOOL_TYPE.DATA_SOURCE) {
          dataSourceFormDrawerRef.value?.open(copiedTool, true)
        } else if (copiedTool.tool_type === TOOL_TYPE.MCP) {
          mcpFormDrawerRef.value?.open(copiedTool, true)
        } else if (copiedTool.tool_type === TOOL_TYPE.SKILL) {
          skillToolFormDrawerRef.value?.open(copiedTool, true)
        } else if (copiedTool.tool_type === TOOL_TYPE.WORKFLOW) {
          workflowFormDialogRef.value?.open(copiedTool, true)
        } else {
          toolFormDrawerRef.value?.open(copiedTool, true)
        }
      })
    })
    .finally(() => {
      loading.value = false
    })
}

function handleFormClosed() {
  formMounted.value = false
}
</script>

<template>
  <MkDropdownItem @click="handleCopyTool">
    <template #icon><MkIcon name="icon_copy_outlined" /></template>
    <span>{{ label }}</span>
  </MkDropdownItem>

  <template v-if="formMounted">
    <ToolFormDrawer
      v-if="tool.tool_type === TOOL_TYPE.CUSTOM"
      ref="toolFormDrawerRef"
      title="复制工具"
      :api="api"
      :folder-id="tool.folder_id ?? ''"
      @closed="handleFormClosed"
      @refresh="emit('refresh')"
    />
    <DataSourceFormDrawer
      v-else-if="tool.tool_type === TOOL_TYPE.DATA_SOURCE"
      ref="dataSourceFormDrawerRef"
      title="复制数据源"
      :api="api"
      :folder-id="tool.folder_id ?? ''"
      @closed="handleFormClosed"
      @refresh="emit('refresh')"
    />
    <McpFormDrawer
      v-else-if="tool.tool_type === TOOL_TYPE.MCP"
      ref="mcpFormDrawerRef"
      title="复制 MCP"
      :api="api"
      :folder-id="tool.folder_id ?? ''"
      @closed="handleFormClosed"
      @refresh="emit('refresh')"
    />
    <SkillToolFormDrawer
      v-else-if="tool.tool_type === TOOL_TYPE.SKILL"
      ref="skillToolFormDrawerRef"
      title="复制 Skill"
      :api="api"
      :folder-id="tool.folder_id ?? ''"
      @closed="handleFormClosed"
      @refresh="emit('refresh')"
    />
    <WorkflowFormDialog
      v-else-if="tool.tool_type === TOOL_TYPE.WORKFLOW"
      ref="workflowFormDialogRef"
      title="复制工作流"
      :api="api"
      :folder-id="tool.folder_id ?? ''"
      @closed="handleFormClosed"
      @refresh="emit('refresh')"
    />
  </template>
</template>
