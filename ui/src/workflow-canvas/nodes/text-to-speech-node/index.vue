<script setup lang="ts">
import { computed, inject, onMounted, ref, useTemplateRef } from 'vue'

import type { FormInstance } from 'element-plus'
import ModelSelect from '@/components/business/model-select/index.vue'
import NodeCascader from '@/workflow-canvas/core/NodeCascader.vue'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import { useWorkflowStore } from '@/workflow-canvas/store'
import { WorkflowMode } from '@/workflow-canvas/types'
import type { ModelItem, ModelProviderItem } from '@/api/types'

defineOptions({ name: 'WorkflowTextToSpeechNode' })
const getModel = inject('getModel') as () => WorkflowNodeModel
const apiType = (inject('apiType') as string) || 'workspace'
const workflowMode = inject<WorkflowMode>('workflowMode', WorkflowMode.Application)
const model = getModel()

interface TextToSpeechNodeForm {
  tts_model_id: string
  tts_model_id_type: 'custom' | 'default' | 'reference'
  tts_model_id_reference: string[]
  content_list: string[]
  is_result: boolean
  model_params_setting: Record<string, unknown>
}

const formRef = useTemplateRef<FormInstance>('formRef')
const modelCascaderRef = useTemplateRef<InstanceType<typeof NodeCascader>>('modelCascaderRef')
const contentCascaderRef = useTemplateRef<InstanceType<typeof NodeCascader>>('contentCascaderRef')

const store = useWorkflowStore(apiType)
const modelList = ref<Array<ModelItem>>([])
const providerOptions = ref<Array<ModelProviderItem>>([])

const defaultForm: TextToSpeechNodeForm = {
  tts_model_id: '',
  tts_model_id_type: 'default',
  tts_model_id_reference: [],
  content_list: [],
  is_result: true,
  model_params_setting: {},
}
const savedForm = model.properties.node_data as Partial<TextToSpeechNodeForm> | undefined
model.properties.node_data = {
  ...defaultForm,
  ...savedForm,
  tts_model_id_type: savedForm ? (savedForm.tts_model_id_type ?? 'custom') : defaultForm.tts_model_id_type,
  tts_model_id_reference: Array.isArray(savedForm?.tts_model_id_reference) ? savedForm.tts_model_id_reference : [],
  content_list: Array.isArray(savedForm?.content_list) ? savedForm.content_list : [],
  is_result: savedForm ? savedForm.is_result : defaultForm.is_result,
  model_params_setting: savedForm?.model_params_setting ?? {},
}

const formData = computed<TextToSpeechNodeForm>({
  get: () => model.properties.node_data as TextToSpeechNodeForm,
  set: (value) => (model.properties.node_data = value),
})

const modelSetting = computed(() => {
  const defaultModel = model.getDefaultModelConfig('TTS')
  const isDefaultModel = formData.value.tts_model_id_type === 'default'
  return {
    model_id: isDefaultModel ? (defaultModel?.model_id ?? '') : formData.value.tts_model_id,
    model_params_setting: isDefaultModel ? (defaultModel?.model_params_setting ?? {}) : formData.value.model_params_setting,
  }
})
const modelFormProp = computed(() => (formData.value.tts_model_id_type === 'reference' ? 'tts_model_id_reference' : 'tts_model_id'))
const showSettings = computed(() =>
  [WorkflowMode.Application, WorkflowMode.ApplicationLoop, WorkflowMode.Tool, WorkflowMode.ToolLoop].includes(workflowMode),
)

function updateNodeData(setting: Partial<TextToSpeechNodeForm>) {
  model.properties.node_data = { ...formData.value, ...setting }
}

function changeModelSource(source: TextToSpeechNodeForm['tts_model_id_type']) {
  updateNodeData({ tts_model_id_reference: [], tts_model_id_type: source })
}

function validateModel(_rule: unknown, _value: unknown, callback: (error?: Error) => void) {
  if (formData.value.tts_model_id_type === 'reference') {
    callback(formData.value.tts_model_id_reference.length ? undefined : new Error('请选择引用变量'))
    return
  }
  callback(
    modelSetting.value.model_id
      ? undefined
      : new Error(formData.value.tts_model_id_type === 'default' ? '请在默认模型设置中选择语音合成模型' : '请选择语音合成模型'),
  )
}

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
    <h6 class="mk-title-decoration mb-3">节点设置</h6>
    <div class="mk-gray-card">
      <el-form ref="formRef" :model="formData" label-position="top" require-asterisk-position="right" @submit.prevent>
        <el-form-item class="mk-hide-asterisk" :prop="modelFormProp" :rules="{ validator: validateModel, trigger: 'change' }">
          <template #label>
            <div class="flex-between">
              <span class="mk-required">语音合成模型</span>
              <el-select
                :model-value="formData.tts_model_id_type"
                :teleported="false"
                class="w-22!"
                size="small"
                @update:model-value="changeModelSource"
              >
                <el-option label="默认模型" value="default" />
                <el-option label="引用变量" value="reference" />
                <el-option label="自定义" value="custom" />
              </el-select>
            </div>
          </template>
          <ModelSelect
            v-if="formData.tts_model_id_type === 'default'"
            :model-value="modelSetting.model_id"
            :model-params="modelSetting.model_params_setting"
            disabled
            :options="modelList"
            :provider-options="providerOptions"
            placeholder="未配置默认模型"
          />
          <ModelSelect
            v-else-if="formData.tts_model_id_type === 'custom'"
            :model-value="formData.tts_model_id"
            :model-params="formData.model_params_setting"
            can-edit-params
            :options="modelList"
            :provider-options="providerOptions"
            placeholder="请选择语音合成模型"
            @update:model-value="updateNodeData({ tts_model_id: $event })"
            @update:model-params="updateNodeData({ model_params_setting: $event })"
          />
          <NodeCascader
            v-else
            ref="modelCascaderRef"
            :model-value="formData.tts_model_id_reference"
            :node-model="model"
            class="w-full"
            placeholder="请选择变量"
            @update:model-value="updateNodeData({ tts_model_id_reference: $event })"
          />
        </el-form-item>
        <!-- 文本内容 -->
        <el-form-item prop="content_list" :rules="{ required: true, message: '请选择', trigger: 'change' }" label="文本内容">
          <NodeCascader ref="contentCascaderRef" v-model="formData.content_list" :node-model="model" class="w-full" placeholder="请选择" />
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
<style lang="scss" scoped></style>
