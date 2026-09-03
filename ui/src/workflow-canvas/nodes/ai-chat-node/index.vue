<script setup lang="ts">
import { computed, inject, onMounted, ref, useTemplateRef } from 'vue'
import { useRoute } from 'vue-router'
import { cloneDeep, set } from 'lodash'
import type { FormInstance } from 'element-plus'
import { TOOL_TYPE } from '@/api/enums'
import ApplicationApi from '@/api/admin/workspace/application/application'
import SharedApi from '@/api/admin/workspace/shared'
import ToolApi from '@/api/admin/workspace/tool/tool'
import type { ApplicationDetail, ModelItem, ModelProviderItem, ToolItem } from '@/api/types'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import { isLastNode } from '@/workflow-canvas/core/utils'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import { useWorkflowStore } from '@/workflow-canvas/store'
import { WorkflowMode } from '@/workflow-canvas/types'
import HistorySetting from './component/history-setting/index.vue'
import ModelSetting from './component/model-setting/index.vue'
import PromptSetting from './component/prompt-setting/index.vue'
import ReasoningSetting from './component/reasoning-setting/index.vue'
import ResourceSetting from './component/resource-setting/index.vue'
import ResultSetting from './component/result-setting/index.vue'
import VisionSetting from './component/vision-setting/index.vue'
import type {
  AiChatNodeForm,
  AiModelSetting as AiModelSettingValue,
  ApplicationResourceOption,
  HistorySetting as HistorySettingValue,
  PromptSetting as PromptSettingValue,
  ReasoningSetting as ReasoningSettingValue,
  ResourceSetting as ResourceSettingValue,
  ToolResourceOption,
  VisionSetting as VisionSettingValue,
} from './types'

defineOptions({ name: 'WorkflowAiChatNode' })

const getModel = inject('getModel') as () => WorkflowNodeModel
const apiType = (inject('apiType') as string) || 'workspace'
const workflowMode = inject<WorkflowMode>('workflowMode', WorkflowMode.Application)
const model = getModel()
const route = useRoute()
const store = useWorkflowStore(apiType)

const formRef = useTemplateRef<FormInstance>('formRef')
const modelSettingRef = useTemplateRef<InstanceType<typeof ModelSetting>>('modelSettingRef')
const visionSettingRef = useTemplateRef<InstanceType<typeof VisionSetting>>('visionSettingRef')

const modelOptions = ref<ModelItem[]>([])
const providerOptions = ref<ModelProviderItem[]>([])
const toolOptions = ref<ToolResourceOption[]>([])
const mcpOptions = ref<ToolResourceOption[]>([])
const skillOptions = ref<ToolResourceOption[]>([])
const applicationOptions = ref<ApplicationResourceOption[]>([])

const defaultReasoningSetting: ReasoningSettingValue = {
  reasoning_content_enable: false,
  reasoning_content_end: '</think>',
  reasoning_content_start: '<think>',
}

const defaultForm: AiChatNodeForm = {
  application_ids: [],
  dialogue_number: 1,
  dialogue_type: 'WORKFLOW',
  image_list: [],
  is_result: true,
  mcp_output_enable: true,
  mcp_servers: '',
  mcp_source: 'referencing',
  mcp_tool_ids: [],
  model_id: '',
  model_id_reference: [],
  model_id_type: 'default',
  model_params_setting: {},
  model_setting: cloneDeep(defaultReasoningSetting),
  prompt: '{{开始.question}}',
  skill_tool_ids: [],
  system: '',
  tool_ids: [],
  video_list: [],
  vision: false,
}

function normalizeMcpServers(value: unknown) {
  if (!value) return ''
  return typeof value === 'string' ? value : JSON.stringify(value, null, 2)
}

function normalizeForm(data: Partial<AiChatNodeForm> & { mcp_tool_id?: string }) {
  const savedData = cloneDeep(data)
  const normalized = Object.assign(data, cloneDeep(defaultForm), savedData) as AiChatNodeForm & { mcp_tool_id?: string }

  if (!savedData.model_id_type) normalized.model_id_type = 'custom'
  normalized.application_ids = Array.isArray(savedData.application_ids) ? savedData.application_ids : []
  normalized.image_list = Array.isArray(savedData.image_list) ? savedData.image_list : []
  normalized.mcp_tool_ids = Array.isArray(savedData.mcp_tool_ids) ? savedData.mcp_tool_ids : savedData.mcp_tool_id ? [savedData.mcp_tool_id] : []
  normalized.model_id_reference = Array.isArray(savedData.model_id_reference) ? savedData.model_id_reference : []
  normalized.skill_tool_ids = Array.isArray(savedData.skill_tool_ids) ? savedData.skill_tool_ids : []
  normalized.tool_ids = Array.isArray(savedData.tool_ids) ? savedData.tool_ids : []
  normalized.video_list = Array.isArray(savedData.video_list) ? savedData.video_list : []
  normalized.mcp_servers = normalizeMcpServers(savedData.mcp_servers)
  normalized.model_params_setting = savedData.model_params_setting ?? {}
  normalized.model_setting = { ...cloneDeep(defaultReasoningSetting), ...(savedData.model_setting ?? {}) }
  normalized.dialogue_number = Number(savedData.dialogue_number ?? 1)
  normalized.dialogue_type = savedData.dialogue_type ?? 'WORKFLOW'
  normalized.mcp_output_enable = savedData.mcp_output_enable ?? true
  normalized.mcp_source = normalized.mcp_servers ? 'custom' : (savedData.mcp_source ?? 'referencing')
  normalized.prompt = savedData.prompt ?? '{{开始.question}}'
  normalized.system = savedData.system ?? ''
  normalized.vision = savedData.vision ?? false
  if (savedData.is_result === undefined) normalized.is_result = isLastNode(model)
  delete normalized.mcp_tool_id
  return normalized
}

const formData = computed<AiChatNodeForm>({
  get: () => {
    if (!model.properties.node_data) set(model.properties, 'node_data', cloneDeep(defaultForm))
    return normalizeForm(model.properties.node_data as Partial<AiChatNodeForm>)
  },
  set: (value) => set(model.properties, 'node_data', value),
})

const modelSetting = computed<AiModelSettingValue>(() => ({
  model_id: formData.value.model_id,
  model_id_reference: formData.value.model_id_reference,
  model_id_type: formData.value.model_id_type,
  model_params_setting: formData.value.model_params_setting,
}))
const promptSetting = computed<PromptSettingValue>(() => ({ prompt: formData.value.prompt, system: formData.value.system }))
const historySetting = computed<HistorySettingValue>(() => ({
  dialogue_number: formData.value.dialogue_number,
  dialogue_type: formData.value.dialogue_type,
}))
const visionSetting = computed<VisionSettingValue>(() => ({
  image_list: formData.value.image_list,
  video_list: formData.value.video_list,
  vision: formData.value.vision,
}))
const resourceSetting = computed<ResourceSettingValue>(() => ({
  application_ids: formData.value.application_ids,
  mcp_output_enable: formData.value.mcp_output_enable,
  mcp_servers: formData.value.mcp_servers,
  mcp_source: formData.value.mcp_source,
  mcp_tool_ids: formData.value.mcp_tool_ids,
  skill_tool_ids: formData.value.skill_tool_ids,
  tool_ids: formData.value.tool_ids,
}))
const applicationId = computed(() => {
  const value = route.params.applicationId
  return Array.isArray(value) ? (value[0] ?? '') : (value ?? '')
})
const showConversationSettings = computed(() =>
  [WorkflowMode.Application, WorkflowMode.ApplicationLoop, WorkflowMode.Tool, WorkflowMode.ToolLoop].includes(workflowMode),
)
const showApplications = computed(() => apiType !== 'systemShare')

function updateModelSetting(setting: AiModelSettingValue) {
  Object.assign(formData.value, setting)
}

function updatePromptSetting(setting: PromptSettingValue) {
  Object.assign(formData.value, setting)
}

function updateHistorySetting(setting: HistorySettingValue) {
  Object.assign(formData.value, setting)
}

function updateVisionSetting(setting: VisionSettingValue) {
  Object.assign(formData.value, setting)
}

function updateResourceSetting(setting: ResourceSettingValue) {
  Object.assign(formData.value, setting)
}

function updateReasoningSetting(setting: ReasoningSettingValue) {
  formData.value.model_setting = setting
}

function uniqueTools(tools: ToolItem[]) {
  return [...new Map(tools.map((tool) => [tool.id, tool])).values()]
}

async function loadResourceOptions() {
  const [workspaceToolsResult, sharedToolsResult, applicationsResult] = await Promise.allSettled([
    ToolApi.getAllTool(),
    SharedApi.getAllTool(),
    ApplicationApi.getAllApplication(),
  ])
  const workspaceTools = workspaceToolsResult.status === 'fulfilled' ? workspaceToolsResult.value : []
  const sharedTools = sharedToolsResult.status === 'fulfilled' ? sharedToolsResult.value : []
  const applications: ApplicationDetail[] = applicationsResult.status === 'fulfilled' ? applicationsResult.value : []
  const tools = uniqueTools([...workspaceTools, ...sharedTools]).filter(({ is_active }) => is_active)

  toolOptions.value = tools.filter(({ tool_type }) => tool_type === TOOL_TYPE.CUSTOM || tool_type === TOOL_TYPE.WORKFLOW)
  mcpOptions.value = tools.filter(({ tool_type }) => tool_type === TOOL_TYPE.MCP)
  skillOptions.value = tools.filter(({ tool_type }) => tool_type === TOOL_TYPE.SKILL)
  applicationOptions.value = applications.filter(({ id, is_publish }) => is_publish && id !== applicationId.value)
}

function validate() {
  return Promise.all([modelSettingRef.value?.validate(), visionSettingRef.value?.validate(), formRef.value?.validate()]).catch((error) =>
    Promise.reject({ node: model, errMessage: error }),
  )
}

onMounted(() => {
  model.validate = validate
  void formData.value
  store.getModelList({ model_type: 'LLM' }).then((models) => (modelOptions.value = models))
  store.getProviderList().then((providers) => (providerOptions.value = providers))
  void loadResourceOptions()
})
</script>

<template>
  <NodeContainer :node-model="model">
    <h6 class="mb-3">节点设置</h6>
    <el-form ref="formRef" :model="formData" label-position="top" require-asterisk-position="right" @submit.prevent>
      <ModelSetting
        ref="modelSettingRef"
        :model-options="modelOptions"
        :node-model="model"
        :provider-options="providerOptions"
        :setting="modelSetting"
        @update="updateModelSetting"
      />

      <PromptSetting :application-id="applicationId" :model-setting="modelSetting" :setting="promptSetting" @update="updatePromptSetting" />

      <HistorySetting v-if="showConversationSettings" :setting="historySetting" @update="updateHistorySetting" />

      <VisionSetting ref="visionSettingRef" :node-model="model" :setting="visionSetting" @update="updateVisionSetting" />

      <ResourceSetting
        :application-options="applicationOptions"
        :mcp-options="mcpOptions"
        :setting="resourceSetting"
        :show-applications="showApplications"
        :skill-options="skillOptions"
        :tool-options="toolOptions"
        @update="updateResourceSetting"
      />

      <ReasoningSetting :setting="formData.model_setting" @update="updateReasoningSetting" />

      <ResultSetting v-if="showConversationSettings" :enabled="formData.is_result" @update:enabled="formData.is_result = $event" />
    </el-form>
  </NodeContainer>
</template>
