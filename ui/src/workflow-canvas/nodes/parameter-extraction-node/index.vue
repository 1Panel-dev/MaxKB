<template>
  <NodeContainer :node-model="model">
    <h6 class="mb-3">节点设置</h6>
    <el-form ref="formRef" :model="formData" label-position="top" hide-required-asterisk @submit.prevent>
      <el-form-item
        v-if="formData.model_id_type === 'reference'"
        prop="model_id_reference"
        :rules="{ required: true, message: '请选择 AI 模型', trigger: 'change' }"
      >
        <template #label>
          <div class="flex-between gap-3 w-full">
            <span>AI 模型<span class="text-danger">*</span></span>
            <el-select v-model="formData.model_id_type" :teleported="false" class="w-30!" size="small" @change="formData.model_id_reference = []">
              <el-option label="引用变量" value="reference" />
              <el-option label="自定义" value="custom" />
            </el-select>
          </div>
        </template>
        <NodeCascader
          ref="modelCascaderRef"
          v-model="formData.model_id_reference"
          :node-model="model"
          class="w-full"
          placeholder="请选择变量"
        />
      </el-form-item>

      <el-form-item
        v-else
        prop="model_id"
        :rules="{ required: true, message: '请选择 AI 模型', trigger: 'change' }"
      >
        <template #label>
          <div class="flex-between gap-3 w-full">
            <span>AI 模型<span class="text-danger">*</span></span>
            <el-select v-model="formData.model_id_type" :teleported="false" class="w-30!" size="small" @change="formData.model_id_reference = []">
              <el-option label="引用变量" value="reference" />
              <el-option label="自定义" value="custom" />
            </el-select>
          </div>
        </template>
        <ModelSelect placeholder="请输入 AI 模型 ID" :options="modelList" :provider-options="providerOptions" v-model="formData.model_id" />
      </el-form-item>

      <el-form-item prop="input_variable" :rules="{ required: true, message: '请选择输入变量', trigger: 'change' }">
        <template #label>
          <span>输入变量<span class="text-danger">*</span></span>
        </template>
        <NodeCascader ref="inputVariableCascaderRef" v-model="formData.input_variable" :node-model="model" class="w-full" placeholder="请选择变量" />
      </el-form-item>

      <el-form-item prop="variable_list" :rules="{ required: true, message: '请添加提取参数', trigger: 'blur' }">
        <ParametersFieldTable ref="paramsFieldTableRef" :node-model="model" />
      </el-form-item>
    </el-form>
  </NodeContainer>
</template>
<script setup lang="ts">
import { computed, inject, onMounted, ref, useTemplateRef, watch } from 'vue'
import { set } from 'lodash'
import type { FormInstance } from 'element-plus'
import ModelSelect from '@/components/business/model-select/index.vue'
import NodeCascader from '@/workflow-canvas/core/NodeCascader.vue'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import { useWorkflowStore } from '@/workflow-canvas/store'
import type { BaseNodeModel } from '@logicflow/core'
import type { ModelItem, ModelProviderItem } from '@/api/types'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import ParametersFieldTable from './component/ParametersFieldTable.vue'

defineOptions({ name: 'WorkflowParameterExtractionNode' })
const getModel = inject('getModel') as () => BaseNodeModel
const apiType = (inject('apiType') as string) || 'workspace'
const model = getModel() as WorkflowNodeModel

interface ParameterExtractionForm {
  input_variable: string[]
  model_params_setting: Record<string, unknown>
  model_id: string
  model_id_type: 'custom' | 'reference'
  model_id_reference: string[]
  variable_list: Array<Record<string, unknown>>
}

const formRef = useTemplateRef<FormInstance>('formRef')
const modelCascaderRef = useTemplateRef<InstanceType<typeof NodeCascader>>('modelCascaderRef')
const inputVariableCascaderRef = useTemplateRef<InstanceType<typeof NodeCascader>>('inputVariableCascaderRef')
const paramsFieldTableRef = useTemplateRef<InstanceType<typeof ParametersFieldTable>>('paramsFieldTableRef')

const store = useWorkflowStore(apiType)
const modelList = ref<Array<ModelItem>>([])
const providerOptions = ref<Array<ModelProviderItem>>([])

const formData = computed<ParameterExtractionForm>({
  get: () => {
    if (!model.properties.node_data) {
      set(model.properties, 'node_data', {
        input_variable: [],
        model_params_setting: {},
        model_id: '',
        model_id_type: 'custom',
        model_id_reference: [],
        variable_list: [],
      })
    }
    const data = model.properties.node_data as ParameterExtractionForm
    if (data.model_id_type === undefined) set(data, 'model_id_type', 'custom')
    if (!Array.isArray(data.model_id_reference)) set(data, 'model_id_reference', [])
    if (!data.model_params_setting) set(data, 'model_params_setting', {})
    const shouldInit = data.input_variable !== undefined || data.variable_list !== undefined
    if (shouldInit) {
      if (!Array.isArray(data.input_variable)) set(data, 'input_variable', [])
      if (!Array.isArray(data.variable_list)) set(data, 'variable_list', [])
    }
    return data
  },
  set: (value) => (model.properties.node_data = value),
})

watch(
  () => [formData.value.model_id, formData.value.model_id_reference],
  () => {
    const isReference = formData.value.model_id_type === 'reference'
    const targetProp = isReference ? 'model_id_reference' : 'model_id'
    const hasValue = isReference ? formData.value.model_id_reference.length > 0 : Boolean(formData.value.model_id)
    if (hasValue) {
      formRef.value?.clearValidate(targetProp)
    }
  },
)

function validate() {
  const list: Array<Promise<unknown>> = []
  const formResult = formRef.value?.validate()
  if (formResult) list.push(formResult)
  if (formData.value.model_id_type === 'reference') {
    const r = modelCascaderRef.value?.validate()
    if (r) list.push(r)
  }
  const inputR = inputVariableCascaderRef.value?.validate()
  if (inputR) list.push(inputR)
  if (!formData.value.variable_list.length) {
    list.push(Promise.reject('请添加提取参数'))
  }
  return Promise.all(list).catch((error) => Promise.reject({ node: model, errMessage: error }))
}

onMounted(() => {
  set(model, 'validate', validate)
  store.getModelList({ model_type: 'LLM' }).then((data) => {
    modelList.value = data
  })
  store.getProviderList().then((data) => {
    providerOptions.value = data
  })
})
</script>
<style lang="scss" scoped>
:deep(.el-form-item) {
  margin-bottom: 16px;
}
</style>
