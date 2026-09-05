<script setup lang="ts">
import { computed, inject, onMounted, ref, useTemplateRef } from 'vue'

import type { FormInstance } from 'element-plus'
import ModelSelect from '@/components/business/model-select/index.vue'
import { fileTooltip } from '@/workflow-canvas/config/constants'
import NodeCascader from '@/workflow-canvas/core/NodeCascader.vue'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import { useWorkflowStore } from '@/workflow-canvas/store'
import { WorkflowMode } from '@/workflow-canvas/types'
import type { ModelItem, ModelProviderItem } from '@/api/types'

defineOptions({ name: 'WorkflowSpeechToTextNode' })
const getModel = inject('getModel') as () => WorkflowNodeModel
const apiType = (inject('apiType') as string) || 'workspace'
const workflowMode = inject<WorkflowMode>('workflowMode', WorkflowMode.Application)
const model = getModel()

interface SpeechToTextNodeForm {
  stt_model_id: string
  stt_model_id_type: 'custom' | 'default' | 'reference'
  stt_model_id_reference: string[]
  audio_list: string[]
  is_result: boolean
  model_params_setting: Record<string, unknown>
}

const formRef = useTemplateRef<FormInstance>('formRef')
const modelCascaderRef = useTemplateRef<InstanceType<typeof NodeCascader>>('modelCascaderRef')
const contentCascaderRef = useTemplateRef<InstanceType<typeof NodeCascader>>('contentCascaderRef')

const store = useWorkflowStore(apiType)
const modelList = ref<Array<ModelItem>>([])
const providerOptions = ref<Array<ModelProviderItem>>([])

const defaultForm: SpeechToTextNodeForm = {
  stt_model_id: '',
  stt_model_id_type: 'default',
  stt_model_id_reference: [],
  audio_list: [],
  is_result: true,
  model_params_setting: {},
}
const savedForm = model.properties.node_data as Partial<SpeechToTextNodeForm> | undefined
model.properties.node_data = {
  ...defaultForm,
  ...savedForm,
  stt_model_id_type: savedForm ? (savedForm.stt_model_id_type ?? 'custom') : defaultForm.stt_model_id_type,
  stt_model_id_reference: Array.isArray(savedForm?.stt_model_id_reference) ? savedForm.stt_model_id_reference : [],
  audio_list: Array.isArray(savedForm?.audio_list) ? savedForm.audio_list : [],
  is_result: savedForm ? savedForm.is_result : defaultForm.is_result,
  model_params_setting: savedForm?.model_params_setting ?? {},
}

const formData = computed<SpeechToTextNodeForm>({
  get: () => model.properties.node_data as SpeechToTextNodeForm,
  set: (value) => (model.properties.node_data = value),
})

const modelSetting = computed(() => {
  const defaultModel = model.getDefaultModelConfig('STT')
  const isDefaultModel = formData.value.stt_model_id_type === 'default'
  return {
    model_id: isDefaultModel ? (defaultModel?.model_id ?? '') : formData.value.stt_model_id,
    model_params_setting: isDefaultModel ? (defaultModel?.model_params_setting ?? {}) : formData.value.model_params_setting,
  }
})
const modelFormProp = computed(() => (formData.value.stt_model_id_type === 'reference' ? 'stt_model_id_reference' : 'stt_model_id'))
const showSettings = computed(() =>
  [WorkflowMode.Application, WorkflowMode.ApplicationLoop, WorkflowMode.Tool, WorkflowMode.ToolLoop].includes(workflowMode),
)

function updateNodeData(setting: Partial<SpeechToTextNodeForm>) {
  model.properties.node_data = { ...formData.value, ...setting }
}

function changeModelSource(source: SpeechToTextNodeForm['stt_model_id_type']) {
  updateNodeData({ stt_model_id_reference: [], stt_model_id_type: source })
}

function validateModel(_rule: unknown, _value: unknown, callback: (error?: Error) => void) {
  if (formData.value.stt_model_id_type === 'reference') {
    callback(formData.value.stt_model_id_reference.length ? undefined : new Error('请选择引用变量'))
    return
  }
  callback(
    modelSetting.value.model_id
      ? undefined
      : new Error(formData.value.stt_model_id_type === 'default' ? '请在默认模型设置中选择语音识别模型' : '请选择语音识别模型'),
  )
}

function validate() {
  return Promise.all([
    formData.value.stt_model_id_type === 'reference' ? modelCascaderRef.value?.validate() : Promise.resolve(),
    contentCascaderRef.value?.validate(),
    formRef.value?.validate(),
  ]).catch((error) => Promise.reject({ node: model, errMessage: error }))
}

onMounted(() => {
  model.validate = validate
  store.getModelList({ model_type: 'STT' }).then((data) => {
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
              <span class="mk-required">语音识别模型</span>
              <el-select
                :model-value="formData.stt_model_id_type"
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
            v-if="formData.stt_model_id_type === 'default'"
            :model-value="modelSetting.model_id"
            :model-params="modelSetting.model_params_setting"
            disabled
            :options="modelList"
            :provider-options="providerOptions"
            placeholder="未配置默认模型"
          />
          <ModelSelect
            v-else-if="formData.stt_model_id_type === 'custom'"
            :model-value="formData.stt_model_id"
            :model-params="formData.model_params_setting"
            can-edit-params
            :options="modelList"
            :provider-options="providerOptions"
            placeholder="请选择语音识别模型"
            @update:model-value="updateNodeData({ stt_model_id: $event })"
            @update:model-params="updateNodeData({ model_params_setting: $event })"
          />
          <NodeCascader
            v-else
            ref="modelCascaderRef"
            :model-value="formData.stt_model_id_reference"
            :node-model="model"
            class="w-full"
            placeholder="请选择变量"
            @update:model-value="updateNodeData({ stt_model_id_reference: $event })"
          />
        </el-form-item>

        <!-- 语音文件 -->
        <el-form-item prop="audio_list" :rules="{ required: true, message: '请选择', trigger: 'change' }">
          <template #label>
            <span class="flex items-center gap-1">
              语音文件
              <el-tooltip placement="right">
                <template #content>
                  <div class="font-mono whitespace-pre-wrap">{{ fileTooltip }}</div>
                </template>
                <MkIcon name="icon_info_outlined" class="text-N600!" />
              </el-tooltip>
            </span>
          </template>
          <NodeCascader ref="contentCascaderRef" v-model="formData.audio_list" :node-model="model" class="w-full" placeholder="请选择" />
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
