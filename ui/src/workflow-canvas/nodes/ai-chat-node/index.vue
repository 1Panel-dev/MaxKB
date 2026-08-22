<script setup lang="ts">
import { computed, inject, onMounted, useTemplateRef } from 'vue'

import { set } from 'lodash'
import type { FormInstance } from 'element-plus'
import NodeCascader from '@/workflow-canvas/core/NodeCascader.vue'
import NodeContainer from '@/workflow-canvas/core/NodeContainer.vue'
import type { BaseNodeModel } from '@logicflow/core'

defineOptions({ name: 'WorkflowAiChatNode' })
const getModel = inject('getModel') as () => BaseNodeModel
const model = getModel()
interface AiChatNodeForm {
  model_id: string
  model_id_reference: string[]
  model_id_type: 'custom' | 'reference'
  model_setting: { reasoning_content_enable: boolean }
  prompt: string
  system: string
}

const formRef = useTemplateRef<FormInstance>('formRef')
const nodeCascaderRef = useTemplateRef<InstanceType<typeof NodeCascader>>('nodeCascaderRef')

const formData = computed<AiChatNodeForm>({
  get: () => {
    if (!model.properties.node_data) {
      model.properties.node_data = {
        model_id: '',
        model_id_reference: [],
        model_id_type: 'custom',
        model_setting: { reasoning_content_enable: false },
        prompt: '{{开始.question}}',
        system: '',
      }
    }
    return model.properties.node_data as AiChatNodeForm
  },
  set: (value) => (model.properties.node_data = value),
})

function validate() {
  return Promise.all([
    formData.value.model_id_type === 'reference'
      ? nodeCascaderRef.value?.validate()
      : Promise.resolve(),
    formRef.value?.validate(),
  ]).catch((error) => Promise.reject({ node: model, errMessage: error }))
}

onMounted(() => set(model, 'validate', validate))
</script>

<template>
  <NodeContainer :node-model="model">
    <h6 class="mb-3">节点设置</h6>
    <el-form
      ref="formRef"
      :model="formData"
      label-position="top"
      require-asterisk-position="right"
      @submit.prevent
    >
      <el-form-item
        :prop="formData.model_id_type === 'reference' ? 'model_id_reference' : 'model_id'"
        :rules="{ required: true, message: '请选择或填写 AI 模型', trigger: 'change' }"
      >
        <template #label>
          <div class="flex-between gap-3 w-full">
            <span>AI 模型</span>
            <el-select
              v-model="formData.model_id_type"
              :teleported="false"
              class="w-30!"
              size="small"
              @change="formData.model_id_reference = []"
            >
              <el-option label="引用变量" value="reference" />
              <el-option label="自定义" value="custom" />
            </el-select>
          </div>
        </template>
        <NodeCascader
          v-if="formData.model_id_type === 'reference'"
          ref="nodeCascaderRef"
          v-model="formData.model_id_reference"
          :node-model="model"
          class="w-full"
          placeholder="请选择变量"
        />
        <el-input v-else v-model="formData.model_id" placeholder="请输入 AI 模型 ID" />
      </el-form-item>

      <el-form-item label="系统提示词">
        <el-input
          v-model="formData.system"
          :rows="4"
          placeholder="系统提示词，可以引用变量，如 {{开始.question}}"
          type="textarea"
        />
      </el-form-item>

      <el-form-item
        label="用户提示词"
        prop="prompt"
        :rules="{ required: true, message: '请输入用户提示词', trigger: 'blur' }"
      >
        <el-input
          v-model="formData.prompt"
          :rows="5"
          placeholder="用户提示词，可以引用变量，如 {{开始.question}}"
          type="textarea"
        />
      </el-form-item>

      <el-form-item label="返回思考过程">
        <el-switch v-model="formData.model_setting.reasoning_content_enable" />
      </el-form-item>
    </el-form>
  </NodeContainer>
</template>
