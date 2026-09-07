<script setup lang="ts">
import { computed, useTemplateRef } from 'vue'
import type { ApplicationResourceOption, ResourceSetting, ToolResourceOption } from '../../types'
import McpSettingDialog from './McpSettingDialog.vue'

defineOptions({ name: 'AiChatNodeResourceSetting' })

const props = withDefaults(
  defineProps<{
    applicationOptions?: ApplicationResourceOption[]
    mcpOptions?: ToolResourceOption[]
    setting: ResourceSetting
    showApplications?: boolean
    skillOptions?: ToolResourceOption[]
    toolOptions?: ToolResourceOption[]
  }>(),
  {
    applicationOptions: () => [],
    mcpOptions: () => [],
    showApplications: true,
    skillOptions: () => [],
    toolOptions: () => [],
  },
)
const emit = defineEmits<{ update: [setting: Partial<ResourceSetting>] }>()

const mcpDialogRef = useTemplateRef<InstanceType<typeof McpSettingDialog>>('mcpDialogRef')

const selectedMcpTools = computed(() =>
  props.setting.mcp_tool_ids.map(
    (id) => props.mcpOptions.find((option) => option.id === id) ?? { id, name: `已选 MCP（${id}）`, tool_type: 'MCP' as const },
  ),
)
const mcpCount = computed(() => props.setting.mcp_tool_ids.length + Number(Boolean(props.setting.mcp_servers)))

const selectedTools = computed(() =>
  props.setting.tool_ids.map(
    (id) => props.toolOptions.find((option) => option.id === id) ?? { id, name: `已选资源（${id}）`, icon: undefined, tool_type: undefined },
  ),
)
const selectedSkills = computed(() =>
  props.setting.skill_tool_ids.map(
    (id) => props.skillOptions.find((option) => option.id === id) ?? { id, name: `已选资源（${id}）`, icon: undefined, tool_type: undefined },
  ),
)
const selectedApplications = computed<ApplicationResourceOption[]>(() =>
  props.setting.application_ids.map((id) => props.applicationOptions.find((option) => option.id === id) ?? { id, name: `已选资源（${id}）` }),
)

function updateSetting(changes: Partial<ResourceSetting>) {
  emit('update', changes)
}

function removeId(field: 'application_ids' | 'mcp_tool_ids' | 'skill_tool_ids' | 'tool_ids', id: string) {
  updateSetting({ [field]: props.setting[field].filter((resourceId) => resourceId !== id) })
}
</script>

<template>
  <div class="space-y-1">
    <!-- MCP -->
    <MkCollapse trigger-class="py-0!">
      <template #label>
        <div class="flex-between min-w-0 flex-1">
          <span
            >MCP<span v-if="mcpCount">（{{ mcpCount }}）</span></span
          >
          <el-button text title="添加 MCP" type="primary" @click.stop="mcpDialogRef?.open(setting)"><MkIcon name="icon_add_outlined" /></el-button>
        </div>
      </template>

      <div v-if="mcpCount" class="mb-2 flex flex-col gap-1">
        <el-card v-for="resource in selectedMcpTools" :key="resource.id" class="small" shadow="never">
          <div class="flex-between">
            <span class="flex min-w-0 items-center gap-2">
              <ToolIcon :icon="resource.icon" :size="20" class="shrink-0 small" :type="resource.tool_type" />
              <span class="truncate" :title="resource.name">{{ resource.name }}</span>
            </span>
            <el-button text title="移除 MCP" @click="removeId('mcp_tool_ids', resource.id)"><MkIcon name="icon_close_outlined" /></el-button>
          </div>
        </el-card>
        <el-card v-if="setting.mcp_servers" class="small" shadow="never">
          <div class="flex-between">
            <span class="flex min-w-0 items-center gap-2">
              <ToolIcon :size="20" class="shrink-0 small" type="MCP" />
              <span>自定义 MCP 服务</span>
            </span>
            <el-button text title="移除自定义 MCP 服务" @click="updateSetting({ mcp_servers: '' })"><MkIcon name="icon_close_outlined" /></el-button>
          </div>
        </el-card>
      </div>
    </MkCollapse>
    <!-- 工具 -->
    <MkCollapse trigger-class="py-1!">
      <template #label>
        <div class="flex-between min-w-0 flex-1">
          <span
            >工具<span v-if="selectedTools.length">（{{ selectedTools.length }}）</span></span
          >
          <el-button link type="primary" title="添加工具" @click.stop="toolDialogRef?.open(setting.tool_ids)">
            <MkIcon name="icon_add_outlined" />
          </el-button>
        </div>
      </template>

      <div v-if="selectedTools.length" class="mb-2 flex flex-col gap-1">
        <el-card v-for="resource in selectedTools" :key="resource.id" class="small" shadow="never">
          <div class="flex-between">
            <span class="flex min-w-0 items-center gap-2">
              <ToolIcon :icon="resource.icon" :size="20" class="shrink-0 small" :type="resource.tool_type" />
              <span class="truncate" :title="resource.name">{{ resource.name }}</span>
            </span>
            <el-button text title="移除工具" @click="removeId('tool_ids', resource.id)"><MkIcon name="icon_close_outlined" /></el-button>
          </div>
        </el-card>
      </div>
    </MkCollapse>
    <!-- Skills -->
    <MkCollapse trigger-class="py-1!">
      <template #label>
        <div class="flex-between min-w-0 flex-1">
          <span
            >Skills<span v-if="selectedSkills.length">（{{ selectedSkills.length }}）</span></span
          >
          <el-button link type="primary" title="添加Skills" @click.stop="skillDialogRef?.open(setting.skill_tool_ids)">
            <MkIcon name="icon_add_outlined" />
          </el-button>
        </div>
      </template>

      <div v-if="selectedSkills.length" class="mb-2 flex flex-col gap-1">
        <el-card v-for="resource in selectedSkills" :key="resource.id" class="small" shadow="never">
          <div class="flex-between">
            <span class="flex min-w-0 items-center gap-2">
              <ToolIcon :icon="resource.icon" :size="20" class="shrink-0 small" :type="resource.tool_type" />
              <span class="truncate" :title="resource.name">{{ resource.name }}</span>
            </span>
            <el-button text title="移除Skills" @click="removeId('skill_tool_ids', resource.id)"><MkIcon name="icon_close_outlined" /></el-button>
          </div>
        </el-card>
      </div>
    </MkCollapse>
    <!-- 智能体 -->
    <MkCollapse v-if="showApplications" trigger-class="py-1!">
      <template #label>
        <div class="flex-between min-w-0 flex-1">
          <span
            >智能体<span v-if="selectedApplications.length">（{{ selectedApplications.length }}）</span></span
          >
          <el-button link type="primary" title="添加智能体" @click.stop="applicationDialogRef?.open(setting.application_ids)">
            <MkIcon name="icon_add_outlined" />
          </el-button>
        </div>
      </template>

      <div v-if="selectedApplications.length" class="mb-2 flex flex-col gap-1">
        <el-card v-for="resource in selectedApplications" :key="resource.id" class="small" shadow="never">
          <div class="flex-between">
            <span class="flex min-w-0 items-center gap-2">
              <ApplicationIcon :icon="resource.icon" :size="20" class="shrink-0 small" />
              <span class="truncate" :title="resource.name">{{ resource.name }}</span>
            </span>
            <el-button text title="移除智能体" @click="removeId('application_ids', resource.id)"><MkIcon name="icon_close_outlined" /></el-button>
          </div>
        </el-card>
      </div>
    </MkCollapse>
  </div>

  <!-- <McpSettingDialog ref="mcpDialogRef" :options="mcpOptions" @submit="updateSetting" /> -->
</template>
