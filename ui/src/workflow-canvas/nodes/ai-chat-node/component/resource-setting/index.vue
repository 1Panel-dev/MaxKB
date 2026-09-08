<script setup lang="ts">
import { computed, nextTick, ref, useTemplateRef } from 'vue'
import { useRoute } from 'vue-router'
import { cloneDeep } from 'lodash'
import { TOOL_TYPE } from '@/api/enums'
import type { ApplicationDetail, ToolItem } from '@/api/types'
import SelectApplicationDialog from '@/components/business/select-application-dialog/index.vue'
import SelectToolDialog from '@/components/business/select-tool-dialog/index.vue'
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

const route = useRoute()
const toolDialogRef = useTemplateRef<InstanceType<typeof SelectToolDialog>>('toolDialogRef')
const selectingSkills = ref(false)
const applicationDialogRef = useTemplateRef<InstanceType<typeof SelectApplicationDialog>>('applicationDialogRef')
const excludedToolIds = computed(() => (typeof route.params.toolId === 'string' ? [route.params.toolId] : []))
const excludedApplicationIds = computed(() => (typeof route.params.applicationId === 'string' ? [route.params.applicationId] : []))

// 等待标题和类型 Props 更新后再打开，确保查询使用本次选择的资源类型。
function openToolDialog(skills: boolean) {
  selectingSkills.value = skills
  nextTick(() => toolDialogRef.value?.open(skills ? selectedSkills.value : selectedTools.value))
}

function submitToolDialog(tools: (Partial<ToolItem> & { id: string })[]) {
  if (selectingSkills.value) submitSkills(tools)
  else submitTools(tools)
}

// 同时写回执行所需 ID 和回显快照，关闭后再次打开仍保留选择。
function submitTools(tools: (Partial<ToolItem> & { id: string })[]) {
  updateSetting({ tool_ids: tools.map(({ id }) => id), tool_list: cloneDeep(tools) })
}
function submitSkills(tools: (Partial<ToolItem> & { id: string })[]) {
  updateSetting({ skill_tool_ids: tools.map(({ id }) => id), skill_tool_list: cloneDeep(tools) })
}
function submitApplications(applications: (Partial<ApplicationDetail> & { id: string })[]) {
  updateSetting({ application_ids: applications.map(({ id }) => id), application_list: cloneDeep(applications) })
}

const loadedMcpOptions = ref<ToolItem[]>([])
const selectedMcpTools = computed(() =>
  props.setting.mcp_tool_ids.map(
    (id) =>
      loadedMcpOptions.value.find((option) => option.id === id) ??
      props.mcpOptions.find((option) => option.id === id) ?? { id, name: `已选 MCP（${id}）`, tool_type: 'MCP' as const },
  ),
)
const mcpCount = computed(() => props.setting.mcp_tool_ids.length + Number(Boolean(props.setting.mcp_servers)))

const selectedTools = computed(() =>
  props.setting.tool_ids.map((id) => {
    const tool = props.toolOptions.find((option) => option.id === id) ?? props.setting.tool_list?.find((option) => option.id === id)
    return { ...tool, id, icon: tool?.icon, tool_type: tool?.tool_type, name: tool?.name || `已选资源（${id}）` }
  }),
)
const selectedSkills = computed(() =>
  props.setting.skill_tool_ids.map((id) => {
    const tool = props.skillOptions.find((option) => option.id === id) ?? props.setting.skill_tool_list?.find((option) => option.id === id)
    return { ...tool, id, icon: tool?.icon, tool_type: tool?.tool_type, name: tool?.name || `已选资源（${id}）` }
  }),
)
const selectedApplications = computed(() =>
  props.setting.application_ids.map((id) => {
    const application =
      props.applicationOptions.find((option) => option.id === id) ?? props.setting.application_list?.find((option) => option.id === id)
    return { ...application, id, icon: application?.icon, name: application?.name || `已选资源（${id}）` }
  }),
)

function updateSetting(changes: Partial<ResourceSetting>) {
  emit('update', changes)
}

function removeId(field: 'application_ids' | 'mcp_tool_ids' | 'skill_tool_ids' | 'tool_ids', id: string) {
  if (field === 'tool_ids') return submitTools(selectedTools.value.filter((resource) => resource.id !== id))
  if (field === 'skill_tool_ids') return submitSkills(selectedSkills.value.filter((resource) => resource.id !== id))
  if (field === 'application_ids') return submitApplications(selectedApplications.value.filter((resource) => resource.id !== id))
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
          <el-button text type="primary" title="添加工具" @click.stop="openToolDialog(false)">
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
          <el-button text type="primary" title="添加Skills" @click.stop="openToolDialog(true)">
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
          <el-button text type="primary" title="添加智能体" @click.stop="applicationDialogRef?.open(selectedApplications)">
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

  <SelectToolDialog
    ref="toolDialogRef"
    :title="selectingSkills ? 'Skills' : '工具'"
    :tool-types="selectingSkills ? [TOOL_TYPE.SKILL] : undefined"
    :excluded-ids="excludedToolIds"
    @submit="submitToolDialog"
  />
  <SelectApplicationDialog v-if="showApplications" ref="applicationDialogRef" :excluded-ids="excludedApplicationIds" @submit="submitApplications" />
  <McpSettingDialog ref="mcpDialogRef" @loaded="loadedMcpOptions = $event" @submit="updateSetting" />
</template>
