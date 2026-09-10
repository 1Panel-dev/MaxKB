<script setup lang="ts">
import { computed, inject, onMounted, ref, useTemplateRef } from 'vue'

import type { FormInstance } from 'element-plus'
import NodeModelSelect from '@/workflow-canvas/component/node-model-select/index.vue'
import { fileTooltip } from '@/workflow-canvas/config/constants'
import NodeCascader from '@/workflow-canvas/component/NodeCascader.vue'
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

const showSettings = computed(() =>
  [WorkflowMode.Application, WorkflowMode.ApplicationLoop, WorkflowMode.Tool, WorkflowMode.ToolLoop].includes(workflowMode),
)

function updateNodeData(setting: Partial<SpeechToTextNodeForm>) {
  model.properties.node_data = { ...formData.value, ...setting }
}

async function validate() {
  return formRef.value?.validate().catch((error) => Promise.reject({ node: model, errMessage: error }))
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
    <h6 class="mk-title-decoration mb-2">节点设置</h6>
    <div class="mk-gray-card">
      <el-form ref="formRef" :model="formData" label-position="top" require-asterisk-position="right" @submit.prevent>
        <NodeModelSelect
          :node-model="model"
          :form-data="formData"
          :fields="{ source: 'stt_model_id_type', id: 'stt_model_id', reference: 'stt_model_id_reference', params: 'model_params_setting' }"
          model-type="STT"
          label="语音识别模型"
          :options="modelList"
          :provider-options="providerOptions"
          @update="updateNodeData"
        />

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
          <NodeCascader ref="contentCascaderRef" v-model="formData.audio_list" :node-model="model" placeholder="请选择" />
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
