<template>
  <NodeContainer :node-model="model">
    <h6 class="mb-3">节点设置</h6>
    <el-card shadow="never" class="card-never" style="--el-card-padding: 12px">
      <el-form ref="variableSplittingFormRef" :model="form_data" label-position="top" require-asterisk-position="right" label-width="auto" hide-required-asterisk @submit.prevent>
        <el-form-item prop="input_variable" :rules="{ message: '请选择变量', trigger: 'blur', required: true }">
          <template #label>
            <div class="flex-between">
              <div>输入变量<span class="text-danger">*</span></div>
            </div>
          </template>
          <NodeCascader ref="nodeCascaderRef" :node-model="model" class="w-full" placeholder="请选择变量" v-model="form_data.input_variable" />
        </el-form-item>

        <el-form-item prop="variable_list" :rules="{ message: '请添加拆分变量', trigger: 'blur', required: true }">
          <VariableFieldTable ref="VariableFieldTableRef" :node-model="model" />
        </el-form-item>
      </el-form>
    </el-card>
  </NodeContainer>
</template>
<script setup lang="ts">
import { computed, inject, onMounted, useTemplateRef } from 'vue'
import { set } from 'lodash'
import type { BaseNodeModel } from '@logicflow/core'
import type { FormInstance } from 'element-plus'

import NodeCascader from '@/workflow-canvas/core/NodeCascader.vue'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import VariableFieldTable from './component/VariableFieldTable.vue'

defineOptions({ name: 'WorkflowVariableSplittingNode' })
const getModel = inject('getModel') as () => BaseNodeModel
const model = getModel() as WorkflowNodeModel

if (!model.properties.node_data) {
  model.properties.node_data = { input_variable: [], variable_list: [] }
}
const form_data = computed<{ input_variable: string[]; variable_list: Array<Record<string, unknown>> }>({
  get: () => model.properties.node_data as { input_variable: string[]; variable_list: Array<Record<string, unknown>> },
  set: (value) => {
    set(model.properties, 'node_data', value)
  },
})

const variableSplittingFormRef = useTemplateRef<FormInstance>('variableSplittingFormRef')
const nodeCascaderRef = useTemplateRef<InstanceType<typeof NodeCascader>>('nodeCascaderRef')
const VariableFieldTableRef = useTemplateRef<InstanceType<typeof VariableFieldTable>>('VariableFieldTableRef')

const validate = () => {
  const vList: Array<Promise<unknown>> = []
  const formResult = variableSplittingFormRef.value?.validate()
  if (formResult) vList.push(formResult)
  const cascaderResult = nodeCascaderRef.value?.validate()
  if (cascaderResult) vList.push(cascaderResult)
  if (!form_data.value.variable_list.length) {
    vList.push(Promise.reject('请添加拆分变量'))
  }
  return Promise.all(vList).catch((error) => Promise.reject({ node: model, errMessage: error }))
}

onMounted(() => {
  set(model, 'validate', validate)
})
</script>
<style lang="scss" scoped></style>
