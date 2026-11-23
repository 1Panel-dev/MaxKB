<script setup lang="ts">
import { nextTick, ref, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import type SystemResourceToolApi from '@/api/admin/system/resource-management/tool/tool'
import type SystemSharedToolApi from '@/api/admin/system/shared-resources/tool/tool'
import type ToolApi from '@/api/admin/workspace/tool/tool'
import type { ToolItem } from '@/api/types'
import { TOOL_TYPE } from '@/api/enums'
import DataSourceFormDrawer from '@/views/tool/tool-form/DataSourceFormDrawer.vue'
import McpFormDrawer from '@/views/tool/tool-form/McpFormDrawer.vue'
import SkillToolFormDrawer from '@/views/tool/tool-form/SkillToolFormDrawer.vue'
import WorkflowFormDialog from '@/views/tool/tool-form/WorkflowFormDialog.vue'
import ToolFormDrawer from '@/views/tool/tool-form/tool-custom/ToolFormDrawer.vue'

const { t } = useI18n({ useScope: 'global' })

defineOptions({ name: 'EditToolForm' })

defineProps<{
  api: typeof ToolApi | typeof SystemSharedToolApi | typeof SystemResourceToolApi
}>()

const emit = defineEmits<{ update: [tool: ToolItem] }>()

const tool = ref<ToolItem | null>(null)
const toolFormDrawerRef = useTemplateRef<InstanceType<typeof ToolFormDrawer>>('toolFormDrawerRef')
const dataSourceFormDrawerRef = useTemplateRef<InstanceType<typeof DataSourceFormDrawer>>('dataSourceFormDrawerRef')
const mcpFormDrawerRef = useTemplateRef<InstanceType<typeof McpFormDrawer>>('mcpFormDrawerRef')
const skillToolFormDrawerRef = useTemplateRef<InstanceType<typeof SkillToolFormDrawer>>('skillToolFormDrawerRef')
const workflowFormDialogRef = useTemplateRef<InstanceType<typeof WorkflowFormDialog>>('workflowFormDialogRef')

function open(toolData: ToolItem) {
  tool.value = toolData
  return nextTick(() => {
    if (toolData.tool_type === TOOL_TYPE.DATA_SOURCE) {
      dataSourceFormDrawerRef.value?.open(toolData)
    } else if (toolData.tool_type === TOOL_TYPE.MCP) {
      mcpFormDrawerRef.value?.open(toolData)
    } else if (toolData.tool_type === TOOL_TYPE.SKILL) {
      skillToolFormDrawerRef.value?.open(toolData)
    } else if (toolData.tool_type === TOOL_TYPE.WORKFLOW) {
      workflowFormDialogRef.value?.open(toolData)
    } else {
      toolFormDrawerRef.value?.open(toolData)
    }
  })
}

function handleFormClosed() {
  tool.value = null
}
defineExpose({ open })
</script>

<template>
  <template v-if="tool">
    <DataSourceFormDrawer
      v-if="tool.tool_type === TOOL_TYPE.DATA_SOURCE"
      ref="dataSourceFormDrawerRef"
      :title="t('tool.dataSource.editTitle')"
      :api="api"
      :folder-id="tool.folder_id ?? ''"
      @closed="handleFormClosed"
      @update="emit('update', $event)"
    />
    <McpFormDrawer
      v-else-if="tool.tool_type === TOOL_TYPE.MCP"
      ref="mcpFormDrawerRef"
      :title="t('tool.mcp.editTitle')"
      :api="api"
      :folder-id="tool.folder_id ?? ''"
      @closed="handleFormClosed"
      @update="emit('update', $event)"
    />
    <SkillToolFormDrawer
      v-else-if="tool.tool_type === TOOL_TYPE.SKILL"
      ref="skillToolFormDrawerRef"
      :title="t('tool.skill.editTitle')"
      :api="api"
      :folder-id="tool.folder_id ?? ''"
      @closed="handleFormClosed"
      @update="emit('update', $event)"
    />
    <WorkflowFormDialog
      v-else-if="tool.tool_type === TOOL_TYPE.WORKFLOW"
      ref="workflowFormDialogRef"
      :title="t('tool.workflow.editTitle')"
      :api="api"
      :folder-id="tool.folder_id ?? ''"
      @closed="handleFormClosed"
      @update="emit('update', $event)"
    />
    <ToolFormDrawer
      v-else
      ref="toolFormDrawerRef"
      :title="t('tool.editTitle')"
      :api="api"
      :folder-id="tool.folder_id ?? ''"
      @closed="handleFormClosed"
      @update="emit('update', $event)"
    />
  </template>
</template>
