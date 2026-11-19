<script setup lang="ts">
import { computed, inject, onMounted, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import { useI18n } from 'vue-i18n'
import type { AiChatNodeForm } from './types'
import type { ModelItem, ModelProviderItem } from '@/api/types'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import type { ReasoningSettingData } from '@/workflow-canvas/types'
import type { FormInstance } from 'element-plus'
import NodeCascader from '@/workflow-canvas/component/NodeCascader.vue'
import PromptGenerate from '@/workflow-canvas/component/PromptGenerate.vue'
import ThinkingSetting from '@/workflow-canvas/component/ThinkingSetting.vue'
import NodeModelSelect from '@/workflow-canvas/component/node-model-select/index.vue'
import { FILE_REFERENCE_EXAMPLE, START_NODE_REFERENCES } from '@/workflow-canvas/config/constants'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import { handleNodeWheel, isLastNode } from '@/workflow-canvas/core/utils'
import { useWorkflowStore } from '@/workflow-canvas/store'
import { WorkflowMode } from '@/workflow-canvas/types'
import ResourceSetting from './component/resource-setting/index.vue'

const { t } = useI18n({ useScope: 'global' })

defineOptions({ name: 'WorkflowAiChatNode' })

const getModel = inject('getModel') as () => WorkflowNodeModel
const resourceScope = (inject('resourceScope') as string) || 'workspace'
const workflowMode = inject<WorkflowMode>('workflowMode', WorkflowMode.Application)
const model = getModel()
const store = useWorkflowStore(resourceScope)

const formRef = useTemplateRef<FormInstance>('formRef')

const modelOptions = ref<ModelItem[]>([])
const providerOptions = ref<ModelProviderItem[]>([])

const defaultThinkingSetting: ReasoningSettingData = {
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
  model_setting: cloneDeep(defaultThinkingSetting),
  prompt: START_NODE_REFERENCES.question,
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
    reasoning_content_enable: savedForm?.model_setting?.reasoning_content_enable ?? defaultThinkingSetting.reasoning_content_enable,
    reasoning_content_end: savedForm?.model_setting?.reasoning_content_end ?? defaultThinkingSetting.reasoning_content_end,
    reasoning_content_start: savedForm?.model_setting?.reasoning_content_start ?? defaultThinkingSetting.reasoning_content_start,
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

// 提示词生成使用当前生效的模型；引用变量在运行前无法确定模型。
const promptModelId = computed(() => {
  if (formData.value.model_id_type === 'reference') return ''
  return formData.value.model_id_type === 'default' ? (model.getDefaultModelConfig('LLM')?.model_id ?? '') : formData.value.model_id
})

const showSettings = computed(() =>
  [WorkflowMode.Application, WorkflowMode.ApplicationLoop, WorkflowMode.Tool, WorkflowMode.ToolLoop].includes(workflowMode),
)
function updateNodeData(setting: Partial<AiChatNodeForm>) {
  model.properties.node_data = { ...formData.value, ...setting }
}

async function validate() {
  return formRef.value?.validate().catch((error) => Promise.reject({ node: model, errMessage: error }))
}

onMounted(() => {
  if (formData.value.is_result === undefined && isLastNode(model)) formData.value.is_result = true
  model.validate = validate
  store.getModelListWithShared({ model_type: 'LLM' }).then((models) => (modelOptions.value = models))
  store.getProviderList().then((providers) => (providerOptions.value = providers))
})
</script>

<template>
  <NodeContainer :node-model="model">
    <h6 class="mk-title-decoration mb-2">{{ t('workflow.nodeSettings.title') }}</h6>
    <div class="mk-gray-card">
      <el-form
        ref="formRef"
        :model="formData"
        :validate-on-rule-change="false"
        label-position="top"
        require-asterisk-position="right"
        @submit.prevent
      >
        <!-- AI模型 -->
        <NodeModelSelect
          :node-model="model"
          :form-data="formData"
          model-type="LLM"
          :label="t('workflow.model.label')"
          :options="modelOptions"
          :provider-options="providerOptions"
          @update="updateNodeData"
        />

        <!-- 系统提示词 -->
        <el-form-item>
          <template #label>
            <div class="flex-between">
              <div class="flex-align-center gap-1">
                <span>{{ t('workflow.systemPrompt.label') }}</span>
                <MkTooltip :content="t('workflow.systemPrompt.description')" placement="right">
                  <MkIcon name="icon_info_outlined" class="text-N600!" />
                </MkTooltip>
              </div>
              <!-- 生成系统提示词 -->
              <PromptGenerate :model-id="promptModelId" :model-params-setting="formData.model_params_setting" @replace="formData.system = $event" />
            </div>
          </template>
          <MdEditorMagnify
            v-model="formData.system"
            :placeholder="t('workflow.systemPrompt.placeholder', { reference: START_NODE_REFERENCES.question })"
            :title="t('workflow.systemPrompt.label')"
            @wheel="handleNodeWheel"
          />
        </el-form-item>

        <!-- 用户提示词 -->
        <el-form-item
          class="mk-hide-asterisk"
          prop="prompt"
          :rules="{ whitespace: true, required: true, message: t('workflow.userPrompt.requiredMessage'), trigger: 'blur' }"
        >
          <template #label>
            <span class="flex-align-center gap-1">
              <span class="mk-required">{{ t('workflow.userPrompt.label') }}</span>
              <MkTooltip :content="t('workflow.userPrompt.description')" placement="right">
                <MkIcon name="icon_info_outlined" class="text-N600!" />
              </MkTooltip>
            </span>
          </template>
          <MdEditorMagnify
            v-model="formData.prompt"
            :placeholder="t('workflow.userPrompt.placeholder', { reference: START_NODE_REFERENCES.question })"
            :title="t('workflow.userPrompt.label')"
            @wheel="handleNodeWheel"
          />
        </el-form-item>

        <!-- 历史聊天记录 -->
        <el-form-item v-if="showSettings" prop="dialogue_number">
          <template #label>
            <div class="flex-between">
              <span>{{ t('workflow.history.label') }}</span>
              <!-- 选择历史记录来源 -->
              <el-select v-model="formData.dialogue_type" :teleported="false" class="w-18!" size="small">
                <el-option :label="t('workflow.node.title')" value="NODE" />
                <el-option :label="t('workflow.title')" value="WORKFLOW" />
              </el-select>
            </div>
          </template>
          <el-input-number
            v-model="formData.dialogue_number"
            :min="0"
            :value-on-clear="0"
            controls-position="right"
            align="left"
            :step="1"
            :step-strictly="true"
          />
        </el-form-item>

        <!-- 视觉-->
        <div class="flex-between mb-4">
          <span>{{ t('workflow.aiChat.vision') }}</span>
          <el-switch v-model="formData.vision" size="small" />
        </div>
        <template v-if="formData.vision">
          <el-form-item prop="image_list">
            <template #label>
              <span class="flex-align-center gap-1">
                <span>{{ t('upload.types.image') }}</span>
                <MkTooltip placement="right">
                  <template #content>
                    <div class="font-mono whitespace-pre-wrap">{{ `${t('common.labels.example')}：\n${FILE_REFERENCE_EXAMPLE}` }}</div>
                  </template>
                  <MkIcon name="icon_info_outlined" class="text-N600!" />
                </MkTooltip>
              </span>
            </template>
            <NodeCascader ref="imageCascaderRef" v-model="formData.image_list" :node-model="model" :placeholder="t('common.placeholders.select')" />
          </el-form-item>

          <el-form-item>
            <template #label>
              <span class="flex-align-center gap-1">
                {{ t('upload.types.video') }}
                <MkTooltip placement="right">
                  <template #content>
                    <div class="font-mono whitespace-pre-wrap">{{ `${t('common.labels.example')}：\n${FILE_REFERENCE_EXAMPLE}` }}</div>
                  </template>
                  <MkIcon name="icon_info_outlined" class="text-N600!" />
                </MkTooltip>
              </span>
            </template>
            <NodeCascader v-model="formData.video_list" :node-model="model" :placeholder="t('common.placeholders.select')" />
          </el-form-item>
        </template>

        <!-- 技能 -->

        <div class="flex-between w-full gap-3 mb-2">
          <span>{{ t('application.skills.label') }}</span>
          <el-checkbox :model-value="formData.mcp_output_enable">{{ t('application.skills.outputExecution') }}</el-checkbox>
        </div>
        <div class="mk-white-card w-full">
          <ResourceSetting :setting="formData" @update="updateNodeData" />
        </div>

        <!-- 输出思考 -->
        <div class="flex-between mb-4 mt-4">
          <span>{{ t('workflow.thinking.label') }}</span>
          <div class="flex-align-center gap-2">
            <ThinkingSetting v-model="formData.model_setting" v-if="formData.model_setting.reasoning_content_enable" />
            <el-switch v-model="formData.model_setting.reasoning_content_enable" size="small" />
          </div>
        </div>

        <!-- 返回内容 -->
        <div class="flex-between w-full" v-if="showSettings">
          <span class="flex-align-center gap-1">
            {{ t('workflow.returnContent.label') }}
            <MkTooltip :content="t('workflow.returnContent.description')" placement="right">
              <MkIcon name="icon_info_outlined" class="text-N600!" />
            </MkTooltip>
          </span>
          <span>
            <el-switch v-model="formData.is_result" size="small" />
          </span>
        </div>
      </el-form>
    </div>
  </NodeContainer>
</template>
