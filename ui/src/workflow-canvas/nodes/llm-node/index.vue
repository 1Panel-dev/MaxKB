<script setup lang="ts">
import { computed, inject, onMounted, ref, useTemplateRef } from 'vue'

import type { FormInstance } from 'element-plus'
import type { ModelItem, ModelProviderItem } from '@/api/types'
import NodeCascader from '@/workflow-canvas/component/NodeCascader.vue'
import NodeModelSelect from '@/workflow-canvas/component/node-model-select/index.vue'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import { handleNodeWheel, isLastNode } from '@/workflow-canvas/core/utils'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import { useWorkflowStore } from '@/workflow-canvas/store'
import { WorkflowMode } from '@/workflow-canvas/types'
import ToolsSetting from './component/ToolsSetting.vue'
import { normalizeTool, type LlmTool, type LlmToolsSetting } from './types'

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
  prompt: '{{开始.question}}',
  enable_context: false,
  context_variable: [],
  tools: { location: 'customize', reference: [], tools: [] },
  is_result: false,
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

const showSettings = computed(() =>
  [WorkflowMode.Application, WorkflowMode.ApplicationLoop, WorkflowMode.Tool, WorkflowMode.ToolLoop].includes(workflowMode),
)

function updateNodeData(setting: Partial<LlmNodeForm>) {
  model.properties.node_data = { ...formData.value, ...setting }
}

async function validate() {
  return formRef.value?.validate().catch((error) => Promise.reject({ node: model, errMessage: error }))
}

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
    <h6 class="mk-title-decoration mb-2">节点设置</h6>
    <div class="mk-gray-card">
      <el-form ref="formRef" :model="formData" label-position="top" require-asterisk-position="right" @submit.prevent>
        <NodeModelSelect
          :node-model="model"
          :form-data="formData"
          model-type="LLM"
          label="AI 模型"
          :options="modelList"
          :provider-options="providerOptions"
          @update="updateNodeData"
        />

        <!-- 系统提示词 -->
        <el-form-item>
          <template #label>
            <div class="flex-align-center gap-1">
              <span>系统提示词</span>
              <MkTooltip content="设定模型扮演的角色或遵循的指令" placement="right">
                <MkIcon name="icon_info_outlined" class="text-N600!" />
              </MkTooltip>
            </div>
          </template>
          <MdEditorMagnify
            v-model="formData.system"
            title="系统提示词"
            placeholder="系统提示词，可以引用系统中变量，如 {{开始.question}}"
            @wheel="handleNodeWheel"
          />
        </el-form-item>

        <!-- 用户提示词 -->
        <el-form-item>
          <template #label>
            <div class="flex-align-center gap-1">
              <span>用户提示词</span>
              <MkTooltip content="用户向模型提出的问题或输入的指令" placement="right">
                <MkIcon name="icon_info_outlined" class="text-N600!" />
              </MkTooltip>
            </div>
          </template>
          <MdEditorMagnify
            v-model="formData.prompt"
            title="用户提示词"
            placeholder="用户提示词，可以引用系统中变量，如 {{开始.question}}"
            @wheel="handleNodeWheel"
          />
        </el-form-item>

        <!-- 上下文 -->
        <el-form-item
          class="mk-hide-asterisk"
          prop="context_variable"
          :rules="formData.enable_context ? { type: 'array', required: true, message: '请选择上下文变量', trigger: 'change' } : undefined"
        >
          <template #label>
            <div class="flex-between">
              <span class="flex-align-center gap-1" :class="{ 'mk-required': formData.enable_context }">
                上下文
                <MkTooltip
                  content="开启后引用变量中的消息列表作为上下文，支持 SYSTEM、USER、ASSISTANT、TOOL 内容项或 OpenAI 消息格式"
                  placement="right"
                >
                  <MkIcon name="icon_info_outlined" class="text-N600!" />
                </MkTooltip>
              </span>
              <el-switch v-model="formData.enable_context" size="small" />
            </div>
          </template>
          <NodeCascader
            v-if="formData.enable_context"
            v-model="formData.context_variable"
            :node-model="model"
            class="w-full!"
            placeholder="请选择上下文变量"
          />
        </el-form-item>

        <!-- 工具 -->
        <div class="mb-4">
          <ToolsSetting v-model="formData.tools" :node-model="model" />
        </div>

        <!-- 返回内容 -->
        <div class="flex-between w-full" v-if="showSettings">
          <span class="flex-align-center gap-1">
            返回内容
            <MkTooltip content="关闭后该节点的内容则不输出给用户。如果你想让用户看到该节点的输出内容，请打开开关。" placement="right">
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
