<script setup lang="ts">
import { ref, useTemplateRef } from 'vue'
import type { UploadFile, UploadInstance } from 'element-plus'
import ToolApi from '@/api/admin/workspace/tool/tool'
import { TOOL_TYPE } from '@/api/enums'
import { useStore } from '@/stores'
import { MsgSuccess } from '@/utils/message'
import ToolFormDrawer from '../tool-form/tool-custom/ToolFormDrawer.vue'
import DataSourceFormDrawer from '../tool-form/DataSourceFormDrawer.vue'
import McpFormDrawer from '../tool-form/McpFormDrawer.vue'
import SkillToolFormDrawer from '../tool-form/SkillToolFormDrawer.vue'
import WorkflowFormDialog from '../tool-form/WorkflowFormDialog.vue'

defineOptions({ name: 'ToolCreateDropdown' })

const { auth } = useStore()

const props = defineProps<{ folderId: string }>()

const emit = defineEmits<{ refresh: [] }>()

defineSlots<{
  /** 创建菜单触发器，只能渲染一个有效根节点 */
  trigger?(): unknown
}>()

/* 工具创建表单 */
const toolFormDrawerRef = useTemplateRef<InstanceType<typeof ToolFormDrawer>>('toolFormDrawerRef')
const workflowFormDialogRef = useTemplateRef<InstanceType<typeof WorkflowFormDialog>>('workflowFormDialogRef')
const skillToolFormDrawerRef = useTemplateRef<InstanceType<typeof SkillToolFormDrawer>>('skillToolFormDrawerRef')
const mcpFormDrawerRef = useTemplateRef<InstanceType<typeof McpFormDrawer>>('mcpFormDrawerRef')
const dataSourceFormDrawerRef = useTemplateRef<InstanceType<typeof DataSourceFormDrawer>>('dataSourceFormDrawerRef')

function handleOpenToolForm() {
  toolFormDrawerRef.value?.open()
}

function handleOpenWorkflowForm() {
  workflowFormDialogRef.value?.open()
}

function handleOpenSkillForm() {
  skillToolFormDrawerRef.value?.open()
}

function handleOpenMcpForm() {
  mcpFormDrawerRef.value?.open()
}

function handleOpenDataSourceForm() {
  dataSourceFormDrawerRef.value?.open()
}

/* 导入创建 */
const elUploadRef = ref<UploadInstance>()
function handleImportCreate(file: UploadFile) {
  if (!file.raw) return
  ToolApi.postToolImport(file.raw, props.folderId)
    .then(() => {
      return auth.loadAuthBaseProfile().then(() => {
        MsgSuccess('导入成功')
        handleRefresh()
      })
    })
    .finally(() => {
      elUploadRef.value?.clearFiles()
    })
}

// 发送刷新列表
function handleRefresh() {
  emit('refresh')
}
</script>

<template>
  <MkDropdown trigger="click" placement="bottom-end" persistent>
    <slot name="trigger">
      <el-button type="primary">
        <span class="mr-1">创建</span>
        <MkIcon name="icon_down_outlined" :size="14" />
      </el-button>
    </slot>

    <template #dropdown>
      <MkDropdownMenu class="w-77!">
        <MkDropdownItem class="py-2!" @click="handleOpenToolForm">
          <template #icon><ToolIcon :type="TOOL_TYPE.CUSTOM" /></template>
          <span>工具</span>
        </MkDropdownItem>
        <MkDropdownItem class="py-2!" @click="handleOpenWorkflowForm">
          <template #icon><ToolIcon :type="TOOL_TYPE.WORKFLOW" /></template>
          <span>工作流</span>
        </MkDropdownItem>
        <MkDropdownItem class="py-2!" @click="handleOpenSkillForm">
          <template #icon><ToolIcon :type="TOOL_TYPE.SKILL" /></template>
          <span>Skills</span>
        </MkDropdownItem>
        <MkDropdownItem class="py-2!" @click="handleOpenMcpForm">
          <template #icon><ToolIcon :type="TOOL_TYPE.MCP" /></template>
          <span>MCP</span>
        </MkDropdownItem>
        <MkDropdownItem class="py-2!" @click="handleOpenDataSourceForm">
          <template #icon><ToolIcon :type="TOOL_TYPE.DATA_SOURCE" /></template>
          <span>数据源</span>
        </MkDropdownItem>
        <el-upload ref="elUploadRef" action="#" :auto-upload="false" class="w-full" :file-list="[]" :limit="1" multiple :on-change="handleImportCreate" :show-file-list="false">
          <MkDropdownItem class="py-2!">
            <template #icon>
              <img src="@/assets/mk_icon_import.svg" alt="" />
            </template>
            <span>导入创建</span>
          </MkDropdownItem>
        </el-upload>
      </MkDropdownMenu>
    </template>
  </MkDropdown>
  <ToolFormDrawer ref="toolFormDrawerRef" title="创建工具" :api="ToolApi" :folder-id="folderId" @refresh="handleRefresh" />
  <WorkflowFormDialog ref="workflowFormDialogRef" title="创建工作流" :api="ToolApi" :folder-id="folderId" @refresh="handleRefresh" />
  <SkillToolFormDrawer ref="skillToolFormDrawerRef" title="创建 Skill" :api="ToolApi" :folder-id="folderId" @refresh="handleRefresh" />
  <McpFormDrawer ref="mcpFormDrawerRef" title="创建 MCP" :api="ToolApi" :folder-id="folderId" @refresh="handleRefresh" />
  <DataSourceFormDrawer ref="dataSourceFormDrawerRef" title="创建数据源" :api="ToolApi" :folder-id="folderId" @refresh="handleRefresh" />
</template>
