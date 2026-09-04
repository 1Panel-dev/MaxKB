<script setup lang="ts">
import { computed, inject, onMounted, ref, useTemplateRef } from 'vue'
import { useRoute } from 'vue-router'
import { cloneDeep } from 'lodash'
import type { FormInstance } from 'element-plus'
import type { ModelItem, ModelProviderItem } from '@/api/types'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import { isLastNode } from '@/workflow-canvas/core/utils'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import { useWorkflowStore } from '@/workflow-canvas/store'
import { WorkflowMode } from '@/workflow-canvas/types'
import HistorySetting from './component/history-setting/index.vue'
import ModelSetting from './component/model-setting/index.vue'
import PromptSetting from './component/prompt-setting/index.vue'
import ReasoningSetting from './component/reasoning-setting/index.vue'
import ResultSetting from './component/result-setting/index.vue'
import VisionSetting from './component/vision-setting/index.vue'
import type {
  AiChatNodeForm,
  AiModelSetting as AiModelSettingValue,
  HistorySetting as HistorySettingValue,
  PromptSetting as PromptSettingValue,
  ReasoningSetting as ReasoningSettingValue,
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

// 节点初始化时补齐默认值和兼容旧数据，避免读取表单时改写响应式依赖。
if (!model.properties.node_data) model.properties.node_data = cloneDeep(defaultForm)
normalizeForm(model.properties.node_data as Partial<AiChatNodeForm>)

const formData = computed(() => model.properties.node_data as AiChatNodeForm)

// 默认来源读取保存后的 LLM 配置，节点内保留原有自定义模型和参数。
const modelSetting = computed<AiModelSettingValue>(() => {
  const defaultModel = model.getDefaultModelConfig('LLM')
  const isDefaultModel = formData.value.model_id_type === 'default'
  return {
    model_id: isDefaultModel ? (defaultModel?.model_id ?? '') : formData.value.model_id,
    model_id_reference: formData.value.model_id_reference,
    model_id_type: formData.value.model_id_type,
    model_params_setting: isDefaultModel ? (defaultModel?.model_params_setting ?? {}) : formData.value.model_params_setting,
  }
})
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

const applicationId = computed(() => {
  const value = route.params.applicationId
  return Array.isArray(value) ? (value[0] ?? '') : (value ?? '')
})
const showConversationSettings = computed(() =>
  [WorkflowMode.Application, WorkflowMode.ApplicationLoop, WorkflowMode.Tool, WorkflowMode.ToolLoop].includes(workflowMode),
)

function updateNodeData(setting: Partial<AiChatNodeForm>) {
  model.properties.node_data = { ...formData.value, ...setting }
}


function validate() {
  return Promise.all([modelSettingRef.value?.validate(), visionSettingRef.value?.validate(), formRef.value?.validate()]).catch((error) =>
    Promise.reject({ node: model, errMessage: error }),
  )
}

onMounted(() => {
  model.validate = validate
  store.getModelList({ model_type: 'LLM' }).then((models) => (modelOptions.value = models))
  store.getProviderList().then((providers) => (providerOptions.value = providers))
})
</script>

<template>
  <NodeContainer :node-model="model">
    <h6 class="mk-title-decoration mb-3">节点设置</h6>
    <div class="mk-gray-card">
      <el-form ref="formRef" :model="formData" label-position="top" require-asterisk-position="right" @submit.prevent>
        <!-- AI模型 -->
        <ModelSetting
          ref="modelSettingRef"
          :model-options="modelOptions"
          :node-model="model"
          :provider-options="providerOptions"
          :setting="modelSetting"
          @update="updateNodeData"
        />

        <PromptSetting :application-id="applicationId" :model-setting="modelSetting" :setting="promptSetting" @update="updateNodeData" />

        <HistorySetting v-if="showConversationSettings" :setting="historySetting" @update="updateNodeData" />

        <VisionSetting ref="visionSettingRef" :node-model="model" :setting="visionSetting" @update="updateNodeData" />

        <!-- <ResourceSetting :setting="resourceSetting" :show-applications="showApplications" @update="updateNodeData" /> -->

        <ReasoningSetting :setting="formData.model_setting" @update="updateNodeData" />

        <ResultSetting v-if="showConversationSettings" :enabled="formData.is_result" @update:enabled="formData.is_result = $event" />
      </el-form>
    </div>
  </NodeContainer>
</template>
