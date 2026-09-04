<script setup lang="ts">
import { computed, inject, onMounted, ref, useTemplateRef } from 'vue'

import type { FormInstance } from 'element-plus'
import ModelSelect from '@/components/business/model-select/index.vue'
import NodeCascader from '@/workflow-canvas/core/NodeCascader.vue'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import { useWorkflowStore } from '@/workflow-canvas/store'
import type { BaseNodeModel } from '@logicflow/core'
import type { ModelItem, ModelProviderItem } from '@/api/types'

defineOptions({ name: 'WorkflowTextToSpeechNode' })
const getModel = inject('getModel') as () => BaseNodeModel
const apiType = (inject('apiType') as string) || 'workspace'
const model = getModel()

interface TextToSpeechNodeForm {
  tts_model_id: string
  tts_model_id_type: 'custom' | 'reference'
  tts_model_id_reference: string[]
  content_list: string[]
  model_params_setting: Record<string, unknown>
}

const formRef = useTemplateRef<FormInstance>('formRef')
const modelCascaderRef = useTemplateRef<InstanceType<typeof NodeCascader>>('modelCascaderRef')
const contentCascaderRef = useTemplateRef<InstanceType<typeof NodeCascader>>('contentCascaderRef')

const store = useWorkflowStore(apiType)
const modelList = ref<Array<ModelItem>>([])
const providerOptions = ref<Array<ModelProviderItem>>([])

// 节点初始化时补齐默认值和兼容旧数据，computed 只读取表单。
if (!model.properties.node_data) {
  model.properties.node_data = {
    tts_model_id: '',
    tts_model_id_type: 'custom',
    tts_model_id_reference: [],
    content_list: [],
    model_params_setting: {},
  }
}
const initialNodeData = model.properties.node_data as TextToSpeechNodeForm
if (initialNodeData.tts_model_id_type === undefined) initialNodeData.tts_model_id_type = 'custom'
if (!Array.isArray(initialNodeData.tts_model_id_reference)) initialNodeData.tts_model_id_reference = []
if (!Array.isArray(initialNodeData.content_list)) initialNodeData.content_list = []
if (!initialNodeData.model_params_setting) initialNodeData.model_params_setting = {}

const formData = computed<TextToSpeechNodeForm>({
  get: () => model.properties.node_data as TextToSpeechNodeForm,
  set: (value) => (model.properties.node_data = value),
})

function validate() {
  return Promise.all([
    formData.value.tts_model_id_type === 'reference' ? modelCascaderRef.value?.validate() : Promise.resolve(),
    contentCascaderRef.value?.validate(),
    formRef.value?.validate(),
  ]).catch((error) => Promise.reject({ node: model, errMessage: error }))
}

onMounted(() => {
  model.validate = validate
  store.getModelList({ model_type: 'TTS' }).then((data) => {
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
        :prop="formData.tts_model_id_type === 'reference' ? 'tts_model_id_reference' : 'tts_model_id'"
        :rules="{ required: true, message: '请选择或填写语音合成模型', trigger: 'change' }"
      >
        <template #label>
          <div class="flex-between gap-3 w-full">
            <span>语音合成模型</span>
            <el-select
              v-model="formData.tts_model_id_type"
              :teleported="false"
              class="w-30!"
              size="small"
              @change="formData.tts_model_id_reference = []"
            >
              <el-option label="引用变量" value="reference" />
              <el-option label="自定义" value="custom" />
            </el-select>
          </div>
        </template>
        <NodeCascader
          v-if="formData.tts_model_id_type === 'reference'"
          ref="modelCascaderRef"
          v-model="formData.tts_model_id_reference"
          :node-model="model"
          class="w-full"
          placeholder="请选择变量"
        />
        <ModelSelect
          v-else
          v-model="formData.tts_model_id"
          v-model:model-params="formData.model_params_setting"
          can-edit-params
          :options="modelList"
          :provider-options="providerOptions"
          placeholder="请选择语音合成模型"
        />
      </el-form-item>

      <el-form-item prop="content_list" :rules="{ required: true, message: '请选择文本内容', trigger: 'change' }" label="文本内容">
        <NodeCascader ref="contentCascaderRef" v-model="formData.content_list" :node-model="model" class="w-full" placeholder="选择文本内容" />
      </el-form-item>
    </el-form>
  </NodeContainer>
</template>
<style lang="scss" scoped>
:deep(.el-form-item__label) {
  width: 100%;
}
:deep(.el-form-item) {
  margin-bottom: 16px;
}
</style>
