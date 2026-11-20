<script setup lang="ts">
import { computed, inject, nextTick, onMounted, ref, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import type { LlmTool, LlmToolsSetting } from './types'
import type { ModelItem, ModelProviderItem } from '@/api/types'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import type { FormInstance } from 'element-plus'
import NodeCascader from '@/workflow-canvas/component/NodeCascader.vue'
import PromptGenerate from '@/workflow-canvas/component/PromptGenerate.vue'
import NodeModelSelect from '@/workflow-canvas/component/node-model-select/index.vue'
import { START_NODE_REFERENCES } from '@/workflow-canvas/config/constants'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import { handleNodeWheel, isLastNode } from '@/workflow-canvas/core/utils'
import { useWorkflowStore } from '@/workflow-canvas/store'
import { WorkflowMode } from '@/workflow-canvas/types'
import ToolsSetting from './component/ToolsSetting.vue'
import { normalizeTool } from './types'

const { t } = useI18n({ useScope: 'global' })

defineOptions({ name: 'WorkflowLlmNode' })
const getModel = inject('getModel') as () => WorkflowNodeModel
const resourceScope = (inject('resourceScope') as string) || 'workspace'
const workflowMode = inject<WorkflowMode>('workflowMode', WorkflowMode.Application)
const model = getModel()

interface LlmNodeForm {
  model_id: string
  model_id_reference: string[]
  model_id_type: 'custom' | 'default' | 'reference'
  model_params_setting: Record<string, unknown>
  system: string
  prompt: string
  enable_context: boolean
  context_variable: string[]
  tools: LlmToolsSetting
  is_result?: boolean
}

const formRef = useTemplateRef<FormInstance>('formRef')

const store = useWorkflowStore(resourceScope)
const modelList = ref<Array<ModelItem>>([])
const providerOptions = ref<Array<ModelProviderItem>>([])

const defaultForm: LlmNodeForm = {
  model_id: '',
  model_id_type: 'default',
  model_id_reference: [],
  model_params_setting: {},
  system: '',
  prompt: START_NODE_REFERENCES.question,
  enable_context: false,
  context_variable: [],
  tools: { location: 'customize', reference: [], tools: [] },
  is_result: true,
}
const savedForm = model.properties.node_data as Partial<LlmNodeForm> | undefined
model.properties.node_data = {
  ...defaultForm,
  ...savedForm,
  model_id_type: savedForm ? (savedForm.model_id_type ?? 'custom') : defaultForm.model_id_type,
  model_id_reference: Array.isArray(savedForm?.model_id_reference) ? savedForm.model_id_reference : [],
  model_params_setting: savedForm?.model_params_setting ?? {},
  context_variable: Array.isArray(savedForm?.context_variable) ? savedForm.context_variable : [],
  tools: {
    location: savedForm?.tools?.location === 'reference' ? 'reference' : 'customize',
    reference: Array.isArray(savedForm?.tools?.reference) ? savedForm.tools.reference : [],
    tools: (Array.isArray(savedForm?.tools?.tools) ? savedForm.tools.tools : []).map(normalizeTool).filter((tool): tool is LlmTool => tool !== null),
  },
  is_result: savedForm ? savedForm.is_result : defaultForm.is_result,
}

const formData = computed<LlmNodeForm>({
  get: () => model.properties.node_data as LlmNodeForm,
  set: (value) => (model.properties.node_data = value),
})

// 提示词生成使用当前生效的模型；引用变量时在生成弹窗中选择模型。
const promptModelId = computed(() => {
  if (formData.value.model_id_type === 'reference') return ''
  return formData.value.model_id_type === 'default' ? (model.getDefaultModelConfig('LLM')?.model_id ?? '') : formData.value.model_id
})

const showSettings = computed(() =>
  [WorkflowMode.Application, WorkflowMode.ApplicationLoop, WorkflowMode.Tool, WorkflowMode.ToolLoop].includes(workflowMode),
)

function updateNodeData(setting: Partial<LlmNodeForm>) {
  model.properties.node_data = { ...formData.value, ...setting }
}

function handleContextEnabledChange(enabled: boolean) {
  if (!enabled) void nextTick(() => formRef.value?.clearValidate('context_variable'))
}

async function validate() {
  return formRef.value?.validate().catch((error) => Promise.reject({ node: model, errMessage: error }))
}
const userPromptRequired = computed(() => {
  return formData.value.enable_context ? false : true
})
onMounted(() => {
  if (formData.value.is_result === undefined && isLastNode(model)) formData.value.is_result = true
  model.validate = validate
  store.getModelListWithShared({ model_type: 'LLM' }).then((data) => {
    modelList.value = data
  })
  store.getProviderList().then((data) => {
    providerOptions.value = data
  })
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
        <NodeModelSelect
          :node-model="model"
          :form-data="formData"
          model-type="LLM"
          :label="t('workflow.model.label')"
          :options="modelList"
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
            :title="t('workflow.systemPrompt.label')"
            :placeholder="t('workflow.systemPrompt.placeholder', { reference: START_NODE_REFERENCES.question })"
            @wheel="handleNodeWheel"
          />
        </el-form-item>

        <!-- 用户提示词 -->
        <el-form-item
          class="mk-hide-asterisk"
          prop="prompt"
          :rules="{ whitespace: true, required: userPromptRequired, message: t('workflow.userPrompt.requiredMessage'), trigger: 'blur' }"
        >
          <template #label>
            <div class="flex-align-center gap-1">
              <span class="mk-required">{{ t('workflow.userPrompt.label') }}</span>
              <MkTooltip :content="t('workflow.userPrompt.description')" placement="right">
                <MkIcon name="icon_info_outlined" class="text-N600!" />
              </MkTooltip>
            </div>
          </template>
          <MdEditorMagnify
            v-model="formData.prompt"
            :title="t('workflow.userPrompt.label')"
            :placeholder="t('workflow.userPrompt.placeholder', { reference: START_NODE_REFERENCES.question })"
            @wheel="handleNodeWheel"
          />
        </el-form-item>

        <!-- 上下文 -->
        <el-form-item
          class="mk-hide-asterisk"
          prop="context_variable"
          :rules="
            formData.enable_context
              ? { type: 'array', required: true, message: t('workflow.llm.context.requiredMessage'), trigger: 'change' }
              : undefined
          "
        >
          <template #label>
            <div class="flex-between">
              <span class="flex-align-center gap-1">
                <span :class="{ 'mk-required': formData.enable_context }">{{ t('workflow.llm.context.label') }}</span>

                <MkTooltip :content="t('workflow.llm.context.description')" placement="right">
                  <MkIcon name="icon_info_outlined" class="text-N600!" />
                </MkTooltip>
              </span>
              <!-- 启用上下文 -->
              <el-switch v-model="formData.enable_context" size="small" @change="handleContextEnabledChange" />
            </div>
          </template>
          <NodeCascader
            v-if="formData.enable_context"
            v-model="formData.context_variable"
            :node-model="model"
            class="w-full!"
            :placeholder="t('workflow.llm.context.placeholder')"
          />
        </el-form-item>

        <!-- 工具 -->
        <div class="mb-4">
          <ToolsSetting v-model="formData.tools" :node-model="model" />
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
            <!-- 启用返回内容 -->
            <el-switch v-model="formData.is_result" size="small" />
          </span>
        </div>
      </el-form>
    </div>
  </NodeContainer>
</template>
