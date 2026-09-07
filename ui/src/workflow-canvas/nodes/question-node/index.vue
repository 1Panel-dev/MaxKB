<script setup lang="ts">
import { computed, inject, onMounted, ref, useTemplateRef } from 'vue'

import type { FormInstance } from 'element-plus'
import type { ModelItem, ModelProviderItem } from '@/api/types'
import NodeModelSelect from '@/workflow-canvas/component/node-model-select/index.vue'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import { handleNodeWheel, isLastNode } from '@/workflow-canvas/core/utils'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import { useWorkflowStore } from '@/workflow-canvas/store'
import { WorkflowMode } from '@/workflow-canvas/types'

defineOptions({ name: 'WorkflowQuestionNode' })
const getModel = inject('getModel') as () => WorkflowNodeModel
const apiType = (inject('apiType') as string) || 'workspace'
const workflowMode = inject<WorkflowMode>('workflowMode', WorkflowMode.Application)
const model = getModel()

interface QuestionNodeForm {
  model_id: string
  model_id_reference: string[]
  model_id_type: 'custom' | 'default' | 'reference'
  system: string
  prompt: string
  dialogue_number: number
  is_result: boolean
  model_params_setting: Record<string, unknown>
  dialogue_type: 'NODE' | 'WORKFLOW'
}

const formRef = useTemplateRef<FormInstance>('formRef')

const store = useWorkflowStore(apiType)
const modelList = ref<Array<ModelItem>>([])
const providerOptions = ref<Array<ModelProviderItem>>([])

const defaultForm: QuestionNodeForm = {
  model_id: '',
  model_id_type: 'default',
  model_id_reference: [],
  system:
    '# 角色\n你是一位问题优化大师，擅长根据上下文精准揣测用户意图，并对用户提出的问题进行优化。\n\n' +
    '## 技能\n### 技能 1: 优化问题\n2. 接收用户输入的问题。\n3. 依据上下文仔细分析问题含义。\n4. 输出优化后的问题。\n\n' +
    '## 限制:\n - 仅返回优化后的问题，不进行额外解释或说明。\n - 确保优化后的问题准确反映原始问题意图，不得改变原意。',
  prompt: '{{开始.question}}',
  dialogue_number: 1,
  is_result: false,
  model_params_setting: {},
  dialogue_type: 'NODE',
}
const savedForm = model.properties.node_data as Partial<QuestionNodeForm> | undefined
model.properties.node_data = {
  ...defaultForm,
  ...savedForm,
  model_id_type: savedForm ? (savedForm.model_id_type ?? 'custom') : defaultForm.model_id_type,
  model_id_reference: Array.isArray(savedForm?.model_id_reference) ? savedForm.model_id_reference : [],
  model_params_setting: savedForm?.model_params_setting ?? {},
  system: savedForm?.system ?? defaultForm.system,
  prompt: savedForm?.prompt ?? defaultForm.prompt,
  dialogue_number: savedForm?.dialogue_number ?? defaultForm.dialogue_number,
  dialogue_type: savedForm?.dialogue_type ?? defaultForm.dialogue_type,
  is_result: savedForm ? savedForm.is_result : defaultForm.is_result,
}

const formData = computed<QuestionNodeForm>({
  get: () => model.properties.node_data as QuestionNodeForm,
  set: (value) => (model.properties.node_data = value),
})

const showSettings = computed(() =>
  [WorkflowMode.Application, WorkflowMode.ApplicationLoop, WorkflowMode.Tool, WorkflowMode.ToolLoop].includes(workflowMode),
)

function updateNodeData(setting: Partial<QuestionNodeForm>) {
  model.properties.node_data = { ...formData.value, ...setting }
}

async function validate() {
  return formRef.value?.validate().catch((error) => Promise.reject({ node: model, errMessage: error }))
}

onMounted(() => {
  if (formData.value.is_result === undefined && isLastNode(model)) formData.value.is_result = true
  model.validate = validate
  store.getModelList({ model_type: 'LLM' }).then((data) => {
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
            <div class="flex items-center gap-1">
              <span>系统提示词</span>
              <el-tooltip content="设定模型扮演的角色或遵循的指令" placement="right">
                <MkIcon name="icon_info_outlined" class="text-N600!" />
              </el-tooltip>
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
        <el-form-item class="mk-hide-asterisk" prop="prompt" :rules="{ required: true, message: '请输入用户提示词', trigger: 'blur' }">
          <template #label>
            <div class="flex items-center gap-1">
              <span class="mk-required">用户提示词</span>
              <el-tooltip content="用户向模型提出的问题或输入的指令" placement="right">
                <MkIcon name="icon_info_outlined" class="text-N600!" />
              </el-tooltip>
            </div>
          </template>

          <MdEditorMagnify
            v-model="formData.prompt"
            title="用户提示词"
            placeholder="用户提示词，可以引用系统中变量，如 {{开始.question}}"
            @wheel="handleNodeWheel"
          />
        </el-form-item>

        <!-- 历史聊天记录 -->
        <el-form-item>
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
            :step="1"
            :step-strictly="true"
          />
        </el-form-item>

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
  </NodeContainer>
</template>
