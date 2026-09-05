<script setup lang="ts">
import { computed, inject, onMounted, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance } from 'element-plus'
import type { ModelItem, ModelProviderItem } from '@/api/types'
import ModelSelect from '@/components/business/model-select/index.vue'
import NodeCascader from '@/workflow-canvas/core/NodeCascader.vue'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import { handleNodeWheel, isLastNode } from '@/workflow-canvas/core/utils'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import { useWorkflowStore } from '@/workflow-canvas/store'
import { WorkflowMode } from '@/workflow-canvas/types'
import PromptGenerateDialog from './component/PromptGenerateDialog.vue'
import ReasoningSettingDialog from './component/ReasoningSettingDialog.vue'
import type { AiChatNodeForm, AiModelSetting, AiModelSource, ReasoningSetting } from './types'
import { fileTooltip } from '@/workflow-canvas/config/constants'

defineOptions({ name: 'WorkflowAiChatNode' })

const getModel = inject('getModel') as () => WorkflowNodeModel
const apiType = (inject('apiType') as string) || 'workspace'
const workflowMode = inject<WorkflowMode>('workflowMode', WorkflowMode.Application)
const model = getModel()
const store = useWorkflowStore(apiType)

const formRef = useTemplateRef<FormInstance>('formRef')
const modelCascaderRef = useTemplateRef<InstanceType<typeof NodeCascader>>('modelCascaderRef')
const imageCascaderRef = useTemplateRef<InstanceType<typeof NodeCascader>>('imageCascaderRef')
const promptGenerateDialogRef = useTemplateRef<InstanceType<typeof PromptGenerateDialog>>('promptGenerateDialogRef')
const reasoningSettingDialogRef = useTemplateRef<InstanceType<typeof ReasoningSettingDialog>>('reasoningSettingDialogRef')

const modelOptions = ref<ModelItem[]>([])
const providerOptions = ref<ModelProviderItem[]>([])

const defaultReasoningSetting: ReasoningSetting = {
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

const savedForm = cloneDeep(model.properties.node_data) as (Partial<AiChatNodeForm> & { mcp_tool_id?: string }) | undefined
const mcpServers = normalizeMcpServers(savedForm?.mcp_servers)
const normalizedForm = {
  ...cloneDeep(defaultForm),
  ...savedForm,
  application_ids: Array.isArray(savedForm?.application_ids) ? savedForm.application_ids : [],
  dialogue_number: Number(savedForm?.dialogue_number ?? defaultForm.dialogue_number),
  dialogue_type: savedForm?.dialogue_type ?? defaultForm.dialogue_type,
  image_list: Array.isArray(savedForm?.image_list) ? savedForm.image_list : [],
  is_result: savedForm ? savedForm.is_result : defaultForm.is_result,
  mcp_output_enable: savedForm?.mcp_output_enable ?? defaultForm.mcp_output_enable,
  mcp_servers: mcpServers,
  mcp_source: mcpServers ? 'custom' : (savedForm?.mcp_source ?? defaultForm.mcp_source),
  mcp_tool_ids: Array.isArray(savedForm?.mcp_tool_ids) ? savedForm.mcp_tool_ids : savedForm?.mcp_tool_id ? [savedForm.mcp_tool_id] : [],
  model_id_reference: Array.isArray(savedForm?.model_id_reference) ? savedForm.model_id_reference : [],
  model_id_type: savedForm ? (savedForm.model_id_type ?? 'custom') : defaultForm.model_id_type,
  model_params_setting: savedForm?.model_params_setting ?? {},
  model_setting: {
    reasoning_content_enable: savedForm?.model_setting?.reasoning_content_enable ?? defaultReasoningSetting.reasoning_content_enable,
    reasoning_content_end: savedForm?.model_setting?.reasoning_content_end ?? defaultReasoningSetting.reasoning_content_end,
    reasoning_content_start: savedForm?.model_setting?.reasoning_content_start ?? defaultReasoningSetting.reasoning_content_start,
  },
  prompt: savedForm?.prompt ?? defaultForm.prompt,
  skill_tool_ids: Array.isArray(savedForm?.skill_tool_ids) ? savedForm.skill_tool_ids : [],
  system: savedForm?.system ?? defaultForm.system,
  tool_ids: Array.isArray(savedForm?.tool_ids) ? savedForm.tool_ids : [],
  video_list: Array.isArray(savedForm?.video_list) ? savedForm.video_list : [],
  vision: savedForm?.vision ?? defaultForm.vision,
} as AiChatNodeForm & { mcp_tool_id?: string }
delete normalizedForm.mcp_tool_id
model.properties.node_data = normalizedForm

const formData = computed(() => model.properties.node_data as AiChatNodeForm)

// 默认来源读取保存后的 LLM 配置，节点内保留原有自定义模型和参数。
const modelSetting = computed<AiModelSetting>(() => {
  const defaultModel = model.getDefaultModelConfig('LLM')
  const isDefaultModel = formData.value.model_id_type === 'default'
  return {
    model_id: isDefaultModel ? (defaultModel?.model_id ?? '') : formData.value.model_id,
    model_id_reference: formData.value.model_id_reference,
    model_id_type: formData.value.model_id_type,
    model_params_setting: isDefaultModel ? (defaultModel?.model_params_setting ?? {}) : formData.value.model_params_setting,
  }
})
const modelFormProp = computed(() => (formData.value.model_id_type === 'reference' ? 'model_id_reference' : 'model_id'))

const showSettings = computed(() =>
  [WorkflowMode.Application, WorkflowMode.ApplicationLoop, WorkflowMode.Tool, WorkflowMode.ToolLoop].includes(workflowMode),
)
function updateNodeData(setting: Partial<AiChatNodeForm>) {
  model.properties.node_data = { ...formData.value, ...setting }
}

function changeModelSource(source: AiModelSource) {
  updateNodeData({ model_id_reference: [], model_id_type: source })
}

function validateModel(_rule: unknown, _value: unknown, callback: (error?: Error) => void) {
  const { model_id_type, model_id, model_id_reference } = modelSetting.value
  if (model_id_type === 'reference') {
    callback(model_id_reference.length ? undefined : new Error('请选择引用变量'))
    return
  }
  callback(model_id ? undefined : new Error(model_id_type === 'default' ? '请在默认模型设置中选择 AI 模型' : '请选择 AI 模型'))
}

function validate() {
  return Promise.all([
    formData.value.model_id_type === 'reference' ? modelCascaderRef.value?.validate() : Promise.resolve(),
    formData.value.vision ? imageCascaderRef.value?.validate() : Promise.resolve(),
    formRef.value?.validate(),
  ]).catch((error) => Promise.reject({ node: model, errMessage: error }))
}

onMounted(() => {
  if (formData.value.is_result === undefined && isLastNode(model)) formData.value.is_result = true
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
        <el-form-item class="mk-hide-asterisk" :prop="modelFormProp" :rules="{ validator: validateModel, trigger: 'change' }">
          <template #label>
            <div class="flex-between">
              <span class="mk-required">AI 模型</span>
              <el-select :model-value="formData.model_id_type" :teleported="false" class="w-22!" size="small" @update:model-value="changeModelSource">
                <el-option label="默认模型" value="default" />
                <el-option label="引用变量" value="reference" />
                <el-option label="自定义" value="custom" />
              </el-select>
            </div>
          </template>

          <ModelSelect
            v-if="formData.model_id_type === 'default'"
            :model-value="modelSetting.model_id"
            :model-params="modelSetting.model_params_setting"
            disabled
            :options="modelOptions"
            :provider-options="providerOptions"
            placeholder="未配置默认模型"
          />
          <ModelSelect
            v-else-if="formData.model_id_type === 'custom'"
            :model-value="formData.model_id"
            :model-params="formData.model_params_setting"
            can-edit-params
            :options="modelOptions"
            :provider-options="providerOptions"
            placeholder="请选择 AI 模型"
            @update:model-value="updateNodeData({ model_id: $event })"
            @update:model-params="updateNodeData({ model_params_setting: $event })"
          />
          <NodeCascader
            v-else
            ref="modelCascaderRef"
            :model-value="formData.model_id_reference"
            :node-model="model"
            class="w-full"
            placeholder="请选择变量"
            @update:model-value="updateNodeData({ model_id_reference: $event })"
          />
        </el-form-item>

        <!-- 系统提示词 -->
        <el-form-item>
          <template #label>
            <div class="flex-between">
              <div class="flex items-center gap-1">
                <span>系统提示词</span>
                <el-tooltip content="设定模型扮演的角色或遵循的指令" placement="right">
                  <MkIcon name="icon_info_outlined" class="text-N600!" />
                </el-tooltip>
              </div>
              <!-- // TODO 生成 -->
              <el-button class="-mr-1" text type="primary" :disabled="formData.model_id_type === 'reference' || !formData.model_id">
                <MkIcon name="icon_star" />
              </el-button>
            </div>
          </template>
          <MdEditorMagnify
            v-model="formData.system"
            placeholder="系统提示词，可以引用系统中变量，如{{开始.question}}"
            title="系统提示词"
            @wheel="handleNodeWheel"
          />
        </el-form-item>

        <!-- 用户提示词 -->
        <el-form-item class="mk-hide-asterisk" prop="prompt" :rules="{ required: true, message: '请输入用户提示词', trigger: 'blur' }">
          <template #label>
            <span class="flex items-center gap-1">
              <span class="mk-required">用户提示词</span>
              <el-tooltip content="用户向模型提出的问题或输入的指令" placement="right">
                <MkIcon name="icon_info_outlined" class="text-N600!" />
              </el-tooltip>
            </span>
          </template>
          <MdEditorMagnify
            v-model="formData.prompt"
            placeholder="用户提示词，可以引用系统中变量，如{{开始.question}}"
            title="用户提示词"
            @wheel="handleNodeWheel"
          />
        </el-form-item>

        <!-- 历史聊天记录 -->
        <el-form-item v-if="showSettings" prop="dialogue_number">
          <template #label>
            <div class="flex-between">
              <span>历史聊天记录</span>
              <el-select v-model="formData.dialogue_type" :teleported="false" class="w-18!" size="small">
                <el-option label="节点" value="NODE" />
                <el-option label="工作流" value="WORKFLOW" />
              </el-select>
            </div>
          </template>
          <el-input-number
            v-model="formData.dialogue_number"
            :min="0"
            :value-on-clear="0"
            controls-position="right"
            align="left"
            class="w-full!"
            :step="1"
            :step-strictly="true"
          />
        </el-form-item>

        <!-- 视觉-->
        <div class="flex-between mb-4">
          <span> 视觉 </span>
          <el-switch v-model="formData.vision" size="small" />
        </div>
        <template v-if="formData.vision">
          <el-form-item prop="image_list">
            <template #label>
              <span class="flex items-center gap-1">
                <span>选择图片</span>
                <el-tooltip placement="right">
                  <template #content>
                    <!-- // TODO: ? -->
                    <div class="font-mono whitespace-pre-wrap">{{ fileTooltip }}</div>
                  </template>
                  <MkIcon name="icon_info_outlined" class="text-N600!" />
                </el-tooltip>
              </span>
            </template>
            <NodeCascader ref="imageCascaderRef" v-model="formData.image_list" :node-model="model" class="w-full" placeholder="请选择" />
          </el-form-item>

          <el-form-item>
            <template #label>
              <span class="flex items-center gap-1">
                选择视频
                <el-tooltip placement="right">
                  <template #content>
                    <!-- // TODO: ? -->
                    <div class="font-mono whitespace-pre-wrap">{{ fileTooltip }}</div>
                  </template>
                  <MkIcon name="icon_info_outlined" class="text-N600!" />
                </el-tooltip>
              </span>
            </template>
            <NodeCascader v-model="formData.video_list" :node-model="model" class="w-full" placeholder="请选择" />
          </el-form-item>
        </template>

        <!-- TODO 技能 待处理 -->

        <!-- 输出思考 -->
        <div class="flex-between mb-4">
          <span> 输出思考 </span>
          <div class="flex items-center gap-2">
            <!-- // TODO 思考 -->
            <el-button v-if="formData.model_setting.reasoning_content_enable" text type="primary">
              <MkIcon name="icon-setting" />
            </el-button>
            <el-switch v-model="formData.model_setting.reasoning_content_enable" size="small" />
          </div>
        </div>

        <!-- 返回内容 -->
        <div class="flex-between w-full" v-if="showSettings">
          <span class="flex items-center gap-1">
            返回内容
            <el-tooltip content="关闭后该节点的内容则不输出给用户。如果你想让用户看到该节点的输出内容，请打开开关。" placement="right">
              <MkIcon name="icon_info_outlined" class="text-N600!" />
            </el-tooltip>
          </span>
          <span>
            <el-switch v-model="formData.is_result" size="small" />
          </span>
        </div>
      </el-form>
    </div>

    <PromptGenerateDialog ref="promptGenerateDialogRef" @replace="formData.system = $event" />
    <ReasoningSettingDialog ref="reasoningSettingDialogRef" @submit="formData.model_setting = $event" />
  </NodeContainer>
</template>
