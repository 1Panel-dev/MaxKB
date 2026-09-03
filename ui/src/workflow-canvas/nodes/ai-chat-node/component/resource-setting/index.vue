<script setup lang="ts">
import { computed, ref, useTemplateRef } from 'vue'
import { CaretRight, Close, Plus, QuestionFilled } from '@element-plus/icons-vue'
import type { ApplicationResourceOption, McpSetting, ResourceSetting, ToolResourceOption } from '../../types'
import McpSettingDialog from './McpSettingDialog.vue'
import ResourceGroup from './ResourceGroup.vue'
import ResourceSelectionDialog from './ResourceSelectionDialog.vue'

defineOptions({ name: 'AiChatNodeResourceSetting' })

const props = defineProps<{
  applicationOptions: ApplicationResourceOption[]
  mcpOptions: ToolResourceOption[]
  setting: ResourceSetting
  showApplications: boolean
  skillOptions: ToolResourceOption[]
  toolOptions: ToolResourceOption[]
}>()
const emit = defineEmits<{ update: [setting: ResourceSetting] }>()

const mcpExpanded = ref(true)
const mcpDialogRef = useTemplateRef<InstanceType<typeof McpSettingDialog>>('mcpDialogRef')
const toolDialogRef = useTemplateRef<InstanceType<typeof ResourceSelectionDialog>>('toolDialogRef')
const skillDialogRef = useTemplateRef<InstanceType<typeof ResourceSelectionDialog>>('skillDialogRef')
const applicationDialogRef = useTemplateRef<InstanceType<typeof ResourceSelectionDialog>>('applicationDialogRef')

const selectedMcpTools = computed(() =>
  props.setting.mcp_tool_ids.map(
    (id) => props.mcpOptions.find((option) => option.id === id) ?? { id, name: `已选 MCP（${id}）`, tool_type: 'MCP' as const },
  ),
)
const mcpCount = computed(() => props.setting.mcp_tool_ids.length + Number(Boolean(props.setting.mcp_servers)))

function updateSetting(changes: Partial<ResourceSetting>) {
  emit('update', { ...props.setting, ...changes })
}

function submitMcp(setting: McpSetting) {
  updateSetting(setting)
  mcpExpanded.value = true
}

function removeId(field: 'application_ids' | 'mcp_tool_ids' | 'skill_tool_ids' | 'tool_ids', id: string) {
  updateSetting({ [field]: props.setting[field].filter((resourceId) => resourceId !== id) })
}

function changeMcpOutput(value: boolean | number | string) {
  updateSetting({ mcp_output_enable: Boolean(value) })
}
</script>

<template>
  <el-form-item>
    <template #label>
      <div class="flex-between w-full gap-3">
        <span class="flex items-center gap-1">
          工具与智能体
          <el-tooltip content="允许模型在对话过程中调用 MCP、工具、Skills 和其他智能体" placement="right">
            <MkIcon :icon="QuestionFilled" class="cursor-help text-N600" />
          </el-tooltip>
        </span>
        <el-checkbox :model-value="setting.mcp_output_enable" @change="changeMcpOutput">输出 MCP 过程</el-checkbox>
      </div>
    </template>

    <el-card class="w-full" shadow="never">
      <div>
        <div class="flex-between cursor-pointer py-2" @click="mcpExpanded = !mcpExpanded">
          <span class="flex items-center gap-1 text-N600">
            <MkIcon :icon="CaretRight" class="transition-transform" :class="{ 'rotate-90': mcpExpanded }" />
            MCP<span v-if="mcpCount">（{{ mcpCount }}）</span>
          </span>
          <el-button link title="添加 MCP" type="primary" @click.stop="mcpDialogRef?.open(setting)"><MkIcon :icon="Plus" /></el-button>
        </div>

        <div v-if="mcpExpanded && mcpCount" class="mb-2 flex flex-col gap-1">
          <div v-for="resource in selectedMcpTools" :key="resource.id" class="flex-between rounded-md border border-N200 bg-white px-2 py-1.5">
            <span class="flex min-w-0 items-center gap-2">
              <ToolIcon :icon="resource.icon" :size="20" :type="resource.tool_type" />
              <span class="truncate" :title="resource.name">{{ resource.name }}</span>
            </span>
            <el-button text title="移除" @click="removeId('mcp_tool_ids', resource.id)"><MkIcon :icon="Close" /></el-button>
          </div>
          <div v-if="setting.mcp_servers" class="flex-between rounded-md border border-N200 bg-white px-2 py-1.5">
            <span class="flex min-w-0 items-center gap-2">
              <ToolIcon :size="20" type="MCP" />
              <span>自定义 MCP 服务</span>
            </span>
            <el-button text title="移除" @click="updateSetting({ mcp_servers: '' })"><MkIcon :icon="Close" /></el-button>
          </div>
        </div>
      </div>

      <ResourceGroup
        :ids="setting.tool_ids"
        label="工具"
        :options="toolOptions"
        @add="toolDialogRef?.open(setting.tool_ids)"
        @remove="removeId('tool_ids', $event)"
      />
      <ResourceGroup
        :ids="setting.skill_tool_ids"
        label="Skills"
        :options="skillOptions"
        @add="skillDialogRef?.open(setting.skill_tool_ids)"
        @remove="removeId('skill_tool_ids', $event)"
      />
      <ResourceGroup
        v-if="showApplications"
        application
        :ids="setting.application_ids"
        label="智能体"
        :options="applicationOptions"
        @add="applicationDialogRef?.open(setting.application_ids)"
        @remove="removeId('application_ids', $event)"
      />
    </el-card>
  </el-form-item>

  <McpSettingDialog ref="mcpDialogRef" :options="mcpOptions" @submit="submitMcp" />
  <ResourceSelectionDialog ref="toolDialogRef" title="选择工具" :options="toolOptions" @submit="updateSetting({ tool_ids: $event })" />
  <ResourceSelectionDialog ref="skillDialogRef" title="选择 Skills" :options="skillOptions" @submit="updateSetting({ skill_tool_ids: $event })" />
  <ResourceSelectionDialog
    ref="applicationDialogRef"
    application
    title="选择智能体"
    :options="applicationOptions"
    @submit="updateSetting({ application_ids: $event })"
  />
</template>
