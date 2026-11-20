<script setup lang="ts">
import { computed, inject, onMounted, ref, useTemplateRef } from 'vue'
import { useI18n } from 'vue-i18n'
import type { ModelItem, ModelProviderItem } from '@/api/types'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import type { FormInstance } from 'element-plus'
import NodeCascader from '@/workflow-canvas/component/NodeCascader.vue'
import NodeModelSelect from '@/workflow-canvas/component/node-model-select/index.vue'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import { useWorkflowStore } from '@/workflow-canvas/store'
import { WorkflowMode } from '@/workflow-canvas/types'

defineOptions({ name: 'WorkflowTextToSpeechNode' })
const { t } = useI18n({ useScope: 'global' })
const getModel = inject('getModel') as () => WorkflowNodeModel
const resourceScope = (inject('resourceScope') as string) || 'workspace'
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

const store = useWorkflowStore(resourceScope)
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
  store.getModelListWithShared({ model_type: 'TTS' }).then((data) => {
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
        ref="formRef"
        :model="formData"
        :validate-on-rule-change="false"
        label-position="top"
        require-asterisk-position="right"
        @submit.prevent
      >
        <NodeModelSelect
          :node-model="model"
          :form-data="formData"
          :fields="{ source: 'tts_model_id_type', id: 'tts_model_id', reference: 'tts_model_id_reference', params: 'model_params_setting' }"
          model-type="TTS"
          :label="t('workflow.textToSpeech.model.label')"
          :options="modelList"
          :provider-options="providerOptions"
          @update="updateNodeData"
        />
        <!-- 文本内容 -->
        <el-form-item
          prop="content_list"
          :rules="{ required: true, message: t('common.validation.selectRequired'), trigger: 'change' }"
          :label="t('workflow.textToSpeech.content.label')"
        >
          <NodeCascader ref="contentCascaderRef" v-model="formData.content_list" :node-model="model" :placeholder="t('common.placeholders.select')" />
        </el-form-item>
        <!-- 返回内容 -->
        <div class="flex-between w-full" v-if="showSettings">
          <span class="flex-align-center gap-1">
            {{ t('workflow.returnContent.label') }}
            <MkTooltip :content="t('workflow.returnContent.description')" placement="right">
              <MkIcon name="icon_info_outlined" class="text-N600!" />
            </MkTooltip>
          </span>
          <span>
            <!-- 切换返回内容 -->
            <el-switch v-model="formData.is_result" size="small" />
          </span>
        </div>
      </el-form>
    </div>
  </NodeContainer>
</template>
<style lang="scss" scoped></style>
