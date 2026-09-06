<script setup lang="ts">
import { computed, inject, onBeforeUnmount, onMounted, ref, useTemplateRef } from 'vue'

import type { FormInstance } from 'element-plus'
import ModelSelect from '@/components/business/model-select/index.vue'
import NodeCascader from '@/workflow-canvas/core/NodeCascader.vue'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import { createAnchorGuard, handleNodeWheel } from '@/workflow-canvas/core/utils'
import { useWorkflowStore } from '@/workflow-canvas/store'
import type { BaseNodeModel } from '@logicflow/core'
import type { ModelItem, ModelProviderItem } from '@/api/types'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import ParametersFieldTable from './component/parameters-field/ParametersFieldTable.vue'
import type { ParameterField } from './component/parameters-field/types'

defineOptions({ name: 'WorkflowParameterExtractionNode' })
const getModel = inject('getModel') as () => BaseNodeModel
const apiType = (inject('apiType') as string) || 'workspace'
const model = getModel() as WorkflowNodeModel

interface ParameterExtractionForm {
  input_variable: string[]
  model_params_setting: Record<string, unknown>
  model_id: string
  model_id_type: 'default' | 'custom' | 'reference'
  model_id_reference: string[]
  variable_list: ParameterField[]
}

const parameterExtractionFormRef = useTemplateRef<FormInstance>('parameterExtractionFormRef')

const store = useWorkflowStore(apiType)
const modelList = ref<Array<ModelItem>>([])
const providerOptions = ref<Array<ModelProviderItem>>([])

const defaultForm: ParameterExtractionForm = {
  input_variable: [],
  model_params_setting: {},
  model_id: '',
  model_id_type: 'default',
  model_id_reference: [],
  variable_list: [],
}
const savedForm = model.properties.node_data as Partial<ParameterExtractionForm> | undefined
model.properties.node_data = {
  ...defaultForm,
  ...savedForm,
  model_id: savedForm?.model_id ?? defaultForm.model_id,
  model_id_type: savedForm ? (savedForm.model_id_type ?? 'custom') : defaultForm.model_id_type,
  model_id_reference: Array.isArray(savedForm?.model_id_reference) ? savedForm.model_id_reference : defaultForm.model_id_reference,
  model_params_setting: savedForm?.model_params_setting ?? defaultForm.model_params_setting,
  input_variable: Array.isArray(savedForm?.input_variable) ? savedForm.input_variable : defaultForm.input_variable,
  variable_list: Array.isArray(savedForm?.variable_list) ? savedForm.variable_list : defaultForm.variable_list,
}

const formData = computed<ParameterExtractionForm>({
  get: () => model.properties.node_data as ParameterExtractionForm,
  set: (value) => (model.properties.node_data = value),
})

// 参数表格只编辑列表，节点入口同步输出字段与下游引用。
const parameterList = computed({
  get: () => formData.value.variable_list,
  set: (fields: ParameterField[]) => {
    formData.value.variable_list = fields
    model.properties.config ??= {}
    model.properties.config.fields = [{ label: '结果', value: 'result' }, ...fields.map((field) => ({ label: field.label, value: field.field }))]
    model.clearNextNodeField(false)
  },
})

const modelSetting = computed(() => {
  const defaultModel = model.getDefaultModelConfig('LLM')
  const isDefaultModel = formData.value.model_id_type === 'default'
  return {
    model_id: isDefaultModel ? (defaultModel?.model_id ?? '') : formData.value.model_id,
    model_params_setting: isDefaultModel ? (defaultModel?.model_params_setting ?? {}) : formData.value.model_params_setting,
  }
})
const modelFormProp = computed(() => (formData.value.model_id_type === 'reference' ? 'model_id_reference' : 'model_id'))
function updateNodeData(setting: Partial<ParameterExtractionForm>) {
  model.properties.node_data = { ...formData.value, ...setting }
}

function changeModelSource(source: ParameterExtractionForm['model_id_type']) {
  updateNodeData({ model_id_reference: [], model_id_type: source })
  parameterExtractionFormRef.value?.clearValidate(['model_id', 'model_id_reference'])
}

function validateModel(_rule: unknown, _value: unknown, callback: (error?: Error) => void) {
  if (formData.value.model_id_type === 'reference') {
    callback(formData.value.model_id_reference.length ? undefined : new Error('请选择引用变量'))
    return
  }
  callback(
    modelSetting.value.model_id
      ? undefined
      : new Error(formData.value.model_id_type === 'default' ? '请在默认模型设置中选择 AI 模型' : '请选择 AI 模型'),
  )
}

async function validate() {
  return parameterExtractionFormRef.value?.validate().catch((error) => Promise.reject({ node: model, errMessage: error }))
}

const anchorGuard = createAnchorGuard(model)
onBeforeUnmount(() => anchorGuard.reset())

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
    <h6 class="mk-title-decoration mb-2">节点设置</h6>
    <div class="mk-gray-card">
      <el-form ref="parameterExtractionFormRef" :model="formData" label-position="top" require-asterisk-position="right" @submit.prevent>
        <el-form-item :prop="modelFormProp" class="mk-hide-asterisk" :rules="{ validator: validateModel, trigger: 'change' }">
          <template #label>
            <div class="flex-between gap-3">
              <span class="mk-required">AI 模型</span>
              <el-select
                :model-value="formData.model_id_type"
                :teleported="false"
                class="w-22!"
                size="small"
                @update:model-value="changeModelSource"
                @visible-change="anchorGuard.setOverlayVisible('model-source', $event)"
                @wheel="handleNodeWheel"
              >
                <el-option label="默认模型" value="default" />
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
            placeholder="请选择变量"
          />
          <ModelSelect
            v-else-if="formData.model_id_type === 'default'"
            :model-value="modelSetting.model_id"
            :model-params="modelSetting.model_params_setting"
            disabled
            :options="modelList"
            :provider-options="providerOptions"
            placeholder="未配置默认模型"
          />
          <ModelSelect
            v-else
            :model-value="formData.model_id"
            :model-params="formData.model_params_setting"
            can-edit-params
            :options="modelList"
            :provider-options="providerOptions"
            placeholder="请选择 AI 模型"
            @update:model-value="updateNodeData({ model_id: $event })"
            @update:model-params="updateNodeData({ model_params_setting: $event })"
          />
        </el-form-item>

        <!-- 输入变量 -->
        <el-form-item label="输入变量" prop="input_variable" :rules="{ message: '请选择输入变量', trigger: 'change', required: true }">
          <NodeCascader ref="inputVariableCascaderRef" v-model="formData.input_variable" :node-model="model" placeholder="请选择变量" />
        </el-form-item>

        <!-- 提取参数 -->
        <el-form-item prop="variable_list" :rules="{ type: 'array', message: '请添加提取参数', trigger: 'change', required: true }">
          <ParametersFieldTable v-model="parameterList" />
        </el-form-item>
      </el-form>
    </div>
  </NodeContainer>
</template>
