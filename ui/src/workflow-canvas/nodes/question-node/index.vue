<script setup lang="ts">
import { computed, inject, onMounted, ref, useTemplateRef } from 'vue'
import { QuestionFilled } from '@element-plus/icons-vue'

import type { FormInstance } from 'element-plus'
import ModelSelect from '@/components/business/model-select/index.vue'
import NodeCascader from '@/workflow-canvas/core/NodeCascader.vue'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import { useWorkflowStore } from '@/workflow-canvas/store'
import type { BaseNodeModel } from '@logicflow/core'
import type { ModelItem, ModelProviderItem } from '@/api/types'

defineOptions({ name: 'WorkflowQuestionNode' })
const getModel = inject('getModel') as () => BaseNodeModel
const apiType = (inject('apiType') as string) || 'workspace'
const model = getModel()

interface QuestionNodeForm {
  model_id: string
  model_id_reference: string[]
  model_id_type: 'custom' | 'reference'
  system: string
  prompt: string
  dialogue_type: 'NODE' | 'WORKFLOW'
  dialogue_number: number
  model_params_setting: Record<string, unknown>
}

const formRef = useTemplateRef<FormInstance>('formRef')
const modelCascaderRef = useTemplateRef<InstanceType<typeof NodeCascader>>('modelCascaderRef')

const store = useWorkflowStore(apiType)
const modelList = ref<Array<ModelItem>>([])
const providerOptions = ref<Array<ModelProviderItem>>([])

// 节点初始化时补齐默认值和兼容旧数据，computed 只读取表单。
if (!model.properties.node_data) {
  model.properties.node_data = {
    model_id: '',
    model_id_type: 'custom',
    model_id_reference: [],
    system:
      '# 角色\n你是一位问题优化大师，擅长根据上下文精准揣测用户意图，并对用户提出的问题进行优化。\n\n' +
      '## 技能\n### 技能 1: 优化问题\n2. 接收用户输入的问题。\n3. 依据上下文仔细分析问题含义。\n4. 输出优化后的问题。\n\n' +
      '## 限制:\n - 仅返回优化后的问题，不进行额外解释或说明。\n - 确保优化后的问题准确反映原始问题意图，不得改变原意。',
    prompt: '{{开始.question}}',
    dialogue_type: 'WORKFLOW',
    dialogue_number: 1,
    model_params_setting: {},
  }
}
const initialNodeData = model.properties.node_data as QuestionNodeForm
if (initialNodeData.model_id_type === undefined) initialNodeData.model_id_type = 'custom'
if (!Array.isArray(initialNodeData.model_id_reference)) initialNodeData.model_id_reference = []
if (initialNodeData.system === undefined) initialNodeData.system = ''
if (initialNodeData.prompt === undefined) initialNodeData.prompt = '{{开始.question}}'
if (initialNodeData.dialogue_type === undefined) initialNodeData.dialogue_type = 'WORKFLOW'
if (initialNodeData.dialogue_number === undefined || initialNodeData.dialogue_number === null) {
  initialNodeData.dialogue_number = 1
}
if (!initialNodeData.model_params_setting) initialNodeData.model_params_setting = {}

const formData = computed<QuestionNodeForm>({
  get: () => model.properties.node_data as QuestionNodeForm,
  set: (value) => (model.properties.node_data = value),
})

function validate() {
  return Promise.all([
    formData.value.model_id_type === 'reference' ? modelCascaderRef.value?.validate() : Promise.resolve(),
    formRef.value?.validate(),
  ]).catch((error) => Promise.reject({ node: model, errMessage: error }))
}

onMounted(() => {
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
    <h6 class="mb-3">节点设置</h6>
    <el-form ref="formRef" :model="formData" label-position="top" require-asterisk-position="right" @submit.prevent>
      <el-form-item
        :prop="formData.model_id_type === 'reference' ? 'model_id_reference' : 'model_id'"
        :rules="{ required: true, message: '请选择或填写 AI 模型', trigger: 'change' }"
      >
        <template #label>
          <div class="flex-between gap-3 w-full">
            <span>AI 模型</span>
            <el-select v-model="formData.model_id_type" :teleported="false" class="w-30!" size="small" @change="formData.model_id_reference = []">
              <el-option label="引用变量" value="reference" />
              <el-option label="自定义" value="custom" />
            </el-select>
          </div>
        </template>
        <NodeCascader
          v-if="formData.model_id_type === 'reference'"
          ref="modelCascaderRef"
          v-model="formData.model_id_reference"
          :node-model="model"
          class="w-full"
          placeholder="请选择变量"
        />
        <ModelSelect
          v-else
          v-model="formData.model_id"
          v-model:model-params="formData.model_params_setting"
          can-edit-params
          :options="modelList"
          :provider-options="providerOptions"
          placeholder="请选择 AI 模型"
        />
      </el-form-item>

      <el-form-item>
        <template #label>
          <div class="flex items-center gap-1">
            <span>系统提示词</span>
            <el-tooltip effect="dark" placement="right" content="设定模型扮演的角色或遵循的指令">
              <MkIcon :icon="QuestionFilled" class="cursor-help text-N600" />
            </el-tooltip>
          </div>
        </template>
        <el-input v-model="formData.system" :rows="4" :placeholder="`系统提示词，可以引用变量，如 {{开始.question}}`" type="textarea" />
      </el-form-item>

      <el-form-item label="用户提示词" prop="prompt" :rules="{ required: true, message: '请输入用户提示词', trigger: 'blur' }">
        <template #label>
          <div class="flex items-center gap-1">
            <span>用户提示词</span>
            <el-tooltip effect="dark" placement="right" content="用户向模型提出的问题或输入的指令">
              <MkIcon :icon="QuestionFilled" class="cursor-help text-N600" />
            </el-tooltip>
          </div>
        </template>
        <el-input v-model="formData.prompt" :rows="5" :placeholder="`用户提示词，可以引用变量，如 {{开始.question}}`" type="textarea" />
      </el-form-item>

      <el-form-item label="历史聊天记录">
        <template #label>
          <div class="flex-between gap-3 w-full">
            <span class="whitespace-nowrap">历史聊天记录</span>
            <el-select v-model="formData.dialogue_type" :teleported="false" class="w-20" size="small">
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
          class="w-full!"
          :step="1"
          :step-strictly="true"
        />
      </el-form-item>
    </el-form>
  </NodeContainer>
</template>
<style lang="scss" scoped>
:deep(.el-form-item) {
  margin-bottom: 16px;
}
</style>
