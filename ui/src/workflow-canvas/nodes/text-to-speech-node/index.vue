<script setup lang="ts">
import { computed, inject, onMounted, ref, useTemplateRef } from 'vue'

import type { FormInstance } from 'element-plus'
import NodeModelSelect from '@/workflow-canvas/component/node-model-select/index.vue'
import NodeCascader from '@/workflow-canvas/component/NodeCascader.vue'
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

const showSettings = computed(() =>
  [WorkflowMode.Application, WorkflowMode.ApplicationLoop, WorkflowMode.Tool, WorkflowMode.ToolLoop].includes(workflowMode),
)

function updateNodeData(setting: Partial<TextToSpeechNodeForm>) {
  model.properties.node_data = { ...formData.value, ...setting }
}

async function validate() {
  return formRef.value?.validate().catch((error) => Promise.reject({ node: model, errMessage: error }))
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
    <h6 class="mk-title-decoration mb-2">节点设置</h6>
    <div class="mk-gray-card">
      <el-form ref="formRef" :model="formData" label-position="top" require-asterisk-position="right" @submit.prevent>
        <NodeModelSelect
          :node-model="model"
          :form-data="formData"
          :fields="{ source: 'tts_model_id_type', id: 'tts_model_id', reference: 'tts_model_id_reference', params: 'model_params_setting' }"
          model-type="TTS"
          label="语音合成模型"
          :options="modelList"
          :provider-options="providerOptions"
          @update="updateNodeData"
        />
        <!-- 文本内容 -->
        <el-form-item prop="content_list" :rules="{ required: true, message: '请选择', trigger: 'change' }" label="文本内容">
          <NodeCascader ref="contentCascaderRef" v-model="formData.content_list" :node-model="model" placeholder="请选择" />
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
