<script setup lang="ts">
import { computed, inject, onMounted, ref, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ParameterField } from './component/parameters-field/types'
import type { ModelItem, ModelProviderItem } from '@/api/types'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import type { BaseNodeModel } from '@logicflow/core'
import type { FormInstance } from 'element-plus'
import NodeCascader from '@/workflow-canvas/component/NodeCascader.vue'
import NodeModelSelect from '@/workflow-canvas/component/node-model-select/index.vue'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import { useWorkflowStore } from '@/workflow-canvas/store'
import ParametersFieldTable from './component/parameters-field/ParametersFieldTable.vue'

defineOptions({ name: 'WorkflowParameterExtractionNode' })
const { t } = useI18n({ useScope: 'global' })
const getModel = inject('getModel') as () => BaseNodeModel
const resourceScope = (inject('resourceScope') as string) || 'workspace'
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

const store = useWorkflowStore(resourceScope)
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
    model.properties.config.fields = [
      { label: t('workflow.node.result'), value: 'result' },
      ...fields.map((field) => ({ label: field.label, value: field.field })),
    ]
    model.clearNextNodeField(false)
  },
})

function updateNodeData(setting: Partial<ParameterExtractionForm>) {
  model.properties.node_data = { ...formData.value, ...setting }
}

async function validate() {
  return parameterExtractionFormRef.value?.validate().catch((error) => Promise.reject({ node: model, errMessage: error }))
}

onMounted(() => {
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
    <h6 class="mk-title-decoration mb-2">{{ t('workflow.node.setting') }}</h6>
    <div class="mk-gray-card">
      <el-form
        ref="parameterExtractionFormRef"
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
          :label="t('model.ai.label')"
          :options="modelList"
          :provider-options="providerOptions"
          @update="updateNodeData"
        />

        <!-- 输入变量 -->
        <el-form-item
          :label="t('workflow.variable.input.label')"
          prop="input_variable"
          :rules="{ message: t('workflow.variable.input.requiredMessage'), trigger: 'change', required: true }"
        >
          <NodeCascader
            ref="inputVariableCascaderRef"
            v-model="formData.input_variable"
            :node-model="model"
            :placeholder="t('workflow.variable.selectPlaceholder')"
          />
        </el-form-item>

        <!-- 提取参数 -->
        <el-form-item
          prop="variable_list"
          :rules="{ type: 'array', message: t('workflow.parameterExtraction.parameters.requiredMessage'), trigger: 'change', required: true }"
        >
          <ParametersFieldTable v-model="parameterList" />
        </el-form-item>
      </el-form>
    </div>
  </NodeContainer>
</template>
