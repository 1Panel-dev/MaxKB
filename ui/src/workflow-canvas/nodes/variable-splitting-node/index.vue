<script setup lang="ts">
import { computed, inject, onMounted, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import type { VariableField } from './component/variable-field/types'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import type { BaseNodeModel } from '@logicflow/core'
import type { FormInstance } from 'element-plus'
import NodeCascader from '@/workflow-canvas/component/NodeCascader.vue'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import VariableFieldTable from './component/variable-field/VariableFieldTable.vue'

defineOptions({ name: 'WorkflowVariableSplittingNode' })
const { t } = useI18n({ useScope: 'global' })
const getModel = inject('getModel') as () => BaseNodeModel
const model = getModel() as WorkflowNodeModel

interface VariableSplittingNodeForm {
  input_variable: string[]
  variable_list: VariableField[]
}

const defaultForm: VariableSplittingNodeForm = {
  input_variable: [],
  variable_list: [],
}
const savedForm = model.properties.node_data as Partial<VariableSplittingNodeForm> | undefined
model.properties.node_data = {
  ...defaultForm,
  ...savedForm,
  input_variable: Array.isArray(savedForm?.input_variable) ? savedForm.input_variable : defaultForm.input_variable,
  variable_list: Array.isArray(savedForm?.variable_list) ? savedForm.variable_list : defaultForm.variable_list,
}

const formData = computed<VariableSplittingNodeForm>({
  get: () => model.properties.node_data as VariableSplittingNodeForm,
  set: (value) => (model.properties.node_data = value),
})

const variableSplittingFormRef = useTemplateRef<FormInstance>('variableSplittingFormRef')

// 表格只编辑变量列表；节点输出和下游引用由节点入口同步。
const variableList = computed({
  get: () => formData.value.variable_list,
  set: (fields: VariableField[]) => {
    formData.value.variable_list = fields
    model.properties.config ??= {}
    model.properties.config.fields = [
      { label: t('workflow.node.result'), value: 'result' },
      ...fields.map((field) => ({ label: field.label, value: field.field })),
    ]
    model.clearNextNodeField(false)
  },
})

async function validate() {
  return variableSplittingFormRef.value?.validate().catch((error) => Promise.reject({ node: model, errMessage: error }))
}

onMounted(() => {
  model.validate = validate
})
</script>

<template>
  <NodeContainer :node-model="model">
    <h6 class="mk-title-decoration mb-2">{{ t('workflow.nodeSettings.title') }}</h6>
    <div class="mk-gray-card">
      <el-form
        ref="variableSplittingFormRef"
        :model="formData"
        :validate-on-rule-change="false"
        label-position="top"
        require-asterisk-position="right"
        @submit.prevent
      >
        <!-- 输入变量 -->
        <el-form-item
          :label="t('workflow.variable.input.label')"
          prop="input_variable"
          :rules="{ message: t('workflow.variable.selectRequiredMessage'), trigger: 'change', required: true }"
        >
          <NodeCascader
            ref="nodeCascaderRef"
            :node-model="model"
            :placeholder="t('workflow.variable.selectPlaceholder')"
            v-model="formData.input_variable"
          />
        </el-form-item>
        <!-- 拆分变量 -->
        <el-form-item
          prop="variable_list"
          :rules="{ type: 'array', message: t('workflow.variableSplitting.variables.requiredMessage'), trigger: 'change', required: true }"
        >
          <VariableFieldTable v-model="variableList" />
        </el-form-item>
      </el-form>
    </div>
  </NodeContainer>
</template>
