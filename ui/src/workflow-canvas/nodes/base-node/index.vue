<script setup lang="ts">
import { computed, inject, onMounted, ref, useTemplateRef } from 'vue'
import { cloneDeep, set } from 'lodash'
import type { FormInstance } from 'element-plus'
import type { ModelItem, ModelProviderItem } from '@/api/types'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import { useWorkflowStore } from '@/workflow-canvas/store'
import ApiParameter from './component/api-parameter/index.vue'
import ConversationVariable from './component/conversation-variable/index.vue'
import FileUploadSetting from './component/file-upload/index.vue'
import LongTermMemorySetting from './component/long-term-memory/index.vue'
import SpeechInput from './component/speech-input/index.vue'
import SpeechPlayback from './component/speech-playback/index.vue'
import UserInput from './component/user-input/index.vue'
import {
  defaultFileUploadSetting,
  type ApiInputField,
  type BaseNodeForm,
  type ChatInputField,
  type FileUploadSetting as FileUploadSettingValue,
  type LongTermSetting,
  type SpeechInputSetting,
  type SpeechPlaybackSetting,
  type UserInputField,
  type UserInputSetting,
} from './types'

defineOptions({ name: 'WorkflowBaseNode' })

const getModel = inject('getModel') as () => WorkflowNodeModel
const apiType = (inject('apiType') as string) || 'workspace'
const model = getModel()
const store = useWorkflowStore(apiType)

const formRef = useTemplateRef<FormInstance>('formRef')

const sttModelOptions = ref<ModelItem[]>([])
const ttsModelOptions = ref<ModelItem[]>([])
const llmModelOptions = ref<ModelItem[]>([])
const providerOptions = ref<ModelProviderItem[]>([])

const defaultForm: BaseNodeForm = {
  desc: '',
  file_upload_enable: false,
  file_upload_setting: cloneDeep(defaultFileUploadSetting),
  long_term_enable: false,
  long_term_model_id: '',
  long_term_model_id_type: 'default',
  long_term_model_params_setting: {},
  long_term_trigger_setting: { rounds: 10 },
  long_term_trigger_type: 'ROUND',
  name: '',
  prologue: '您好，我是 XXX 小助手，您可以向我提出 XXX 使用问题。\n- XXX 主要功能有什么？\n- XXX 如何收费？\n- 需要转人工服务',
  stt_autosend: false,
  stt_model_enable: false,
  stt_model_id: '',
  stt_model_id_type: 'default',
  tts_autoplay: false,
  tts_model_enable: false,
  tts_model_id: '',
  tts_model_params_setting: {},
  tts_type: 'BROWSER',
}

function normalizeForm(data: Partial<BaseNodeForm>) {
  const savedData = cloneDeep(data)
  const normalized = Object.assign(data, cloneDeep(defaultForm), savedData) as BaseNodeForm
  normalized.file_upload_setting = { ...cloneDeep(defaultFileUploadSetting), ...(savedData.file_upload_setting ?? {}) }
  normalized.long_term_trigger_setting = savedData.long_term_trigger_setting ?? { rounds: 10 }
  normalized.long_term_model_params_setting = savedData.long_term_model_params_setting ?? {}
  normalized.tts_model_params_setting = savedData.tts_model_params_setting ?? {}
  if (!normalized.stt_model_id_type) normalized.stt_model_id_type = 'default'
  if (!normalized.long_term_model_id_type) normalized.long_term_model_id_type = 'default'
  if (!normalized.tts_type) normalized.tts_type = 'BROWSER'
  if ((normalized.tts_type as string) === 'TTS') normalized.tts_type = 'CUSTOM'
  return normalized
}

const formData = computed<BaseNodeForm>({
  get: () => {
    if (!model.properties.node_data) set(model.properties, 'node_data', cloneDeep(defaultForm))
    return normalizeForm(model.properties.node_data as Partial<BaseNodeForm>)
  },
  set: (value) => set(model.properties, 'node_data', value),
})

function handleEditorWheel(event: WheelEvent) {
  if (event.ctrlKey) event.preventDefault()
  else event.stopPropagation()
}

// 子模块数据映射
const userInputFields = computed(() => (model.properties.user_input_field_list ?? []) as UserInputField[])
const apiInputFields = computed(() => (model.properties.api_input_field_list ?? []) as ApiInputField[])
const conversationVariables = computed(() => (model.properties.chat_input_field_list ?? []) as ChatInputField[])
const userInputSetting = computed<UserInputSetting>(() =>
  cloneDeep((model.properties.user_input_field_list_setting as UserInputSetting | undefined) ?? { exposed_fields: [], menu_title: '更多设置' }),
)
const longTermSetting = computed<LongTermSetting>(() => ({
  long_term_model_id: formData.value.long_term_model_id,
  long_term_model_id_type: formData.value.long_term_model_id_type,
  long_term_model_params_setting: formData.value.long_term_model_params_setting,
  long_term_trigger_setting: formData.value.long_term_trigger_setting,
  long_term_trigger_type: formData.value.long_term_trigger_type,
}))
const speechInputSetting = computed<SpeechInputSetting>(() => ({
  stt_autosend: formData.value.stt_autosend,
  stt_model_enable: formData.value.stt_model_enable,
  stt_model_id: formData.value.stt_model_id,
  stt_model_id_type: formData.value.stt_model_id_type,
}))
const speechPlaybackSetting = computed<SpeechPlaybackSetting>(() => ({
  tts_autoplay: formData.value.tts_autoplay,
  tts_model_enable: formData.value.tts_model_enable,
  tts_model_id: formData.value.tts_model_id,
  tts_model_params_setting: formData.value.tts_model_params_setting,
  tts_type: formData.value.tts_type,
}))

function validateUserFieldReferences() {
  for (const userField of userInputFields.value) {
    for (const condition of userField.visibility_rules?.conditions ?? []) {
      if (!condition.field?.[0] || !condition.field?.[1]) continue
      const isCurrentForm = condition.field[0] === model.id || (model.id === 'base-node' && condition.field[0] === 'global')
      if (isCurrentForm && !userInputFields.value.some(({ field }) => field === condition.field[1])) {
        return Promise.reject('用户输入参数引用了已删除的变量')
      }
    }
  }
  return Promise.resolve()
}

function validate() {
  if (formData.value.tts_model_enable && formData.value.tts_type === 'CUSTOM' && !formData.value.tts_model_id) {
    return Promise.reject({ node: model, errMessage: '请选择语音播放模型' })
  }
  if (formData.value.stt_model_enable && formData.value.stt_model_id_type === 'custom' && !formData.value.stt_model_id) {
    return Promise.reject({ node: model, errMessage: '请选择语音输入模型' })
  }
  if (formData.value.long_term_enable && formData.value.long_term_model_id_type === 'custom' && !formData.value.long_term_model_id) {
    return Promise.reject({ node: model, errMessage: '请选择长期记忆模型' })
  }
  return Promise.all([validateUserFieldReferences(), formRef.value?.validate()]).catch((error) => Promise.reject({ node: model, errMessage: error }))
}

// 子模块数据更新
function updateLongTermEnabled(enabled: boolean) {
  formData.value.long_term_enable = enabled
  if (enabled && !formData.value.long_term_model_id_type) formData.value.long_term_model_id_type = 'default'
  model.graphModel.eventCenter.emit('refreshLongTermConfig', undefined)
}

function updateLongTermSetting(setting: LongTermSetting) {
  Object.assign(formData.value, setting)
  model.graphModel.eventCenter.emit('refreshLongTermConfig', undefined)
}

function updateFileUploadEnabled(enabled: boolean) {
  formData.value.file_upload_enable = enabled
  if (enabled && !formData.value.file_upload_setting) {
    formData.value.file_upload_setting = cloneDeep(defaultFileUploadSetting)
  }
  model.graphModel.eventCenter.emit('refreshFileUploadConfig', undefined)
}

function updateFileUploadSetting(setting: FileUploadSettingValue) {
  formData.value.file_upload_setting = setting
  model.graphModel.eventCenter.emit('refreshFileUploadConfig', undefined)
}

function updateUserInputFields(fields: UserInputField[]) {
  model.properties.user_input_field_list = fields
  model.graphModel.eventCenter.emit('refreshFieldList', undefined)
}

function updateUserInputSetting(setting: UserInputSetting) {
  model.properties.user_input_field_list_setting = setting
}

function updateApiInputFields(fields: ApiInputField[]) {
  model.properties.api_input_field_list = fields
  model.graphModel.eventCenter.emit('refreshFieldList', undefined)
}

function updateConversationVariables(fields: ChatInputField[]) {
  model.properties.chat_input_field_list = fields
  model.graphModel.eventCenter.emit('chatFieldList', undefined)
}

function updateSpeechInput(setting: SpeechInputSetting) {
  Object.assign(formData.value, setting)
}

function updateSpeechPlayback(setting: SpeechPlaybackSetting) {
  Object.assign(formData.value, setting)
}

onMounted(() => {
  model.validate = validate
  if (!Array.isArray(model.properties.user_input_field_list)) model.properties.user_input_field_list = []
  if (!Array.isArray(model.properties.api_input_field_list)) model.properties.api_input_field_list = []
  if (!Array.isArray(model.properties.chat_input_field_list)) model.properties.chat_input_field_list = []
  if (!model.properties.user_input_config) model.properties.user_input_config = { title: '用户输入' }

  store.getModelList({ model_type: 'STT' }).then((models) => (sttModelOptions.value = models))
  store.getModelList({ model_type: 'TTS' }).then((models) => (ttsModelOptions.value = models))
  store.getModelList({ model_type: 'LLM' }).then((models) => (llmModelOptions.value = models))
  store.getProviderList().then((providers) => (providerOptions.value = providers))
})
</script>

<template>
  <NodeContainer :node-model="model">
    <el-form ref="formRef" :model="formData" label-position="top" require-asterisk-position="right" @submit.prevent>
      <el-form-item label="名称" prop="name" :rules="{ required: true, message: '请输入智能体名称', trigger: 'blur' }">
        <el-input
          v-model="formData.name"
          maxlength="64"
          placeholder="请输入智能体名称"
          show-word-limit
          @blur="formData.name = formData.name.trim()"
        />
      </el-form-item>

      <el-form-item label="描述">
        <el-input v-model="formData.desc" maxlength="256" placeholder="描述该智能体的应用场景及用途" :rows="3" show-word-limit type="textarea" />
      </el-form-item>

      <el-form-item label="开场白">
        <MdEditorMagnify v-model="formData.prologue" title="开场白" style="height: 150px" @wheel="handleEditorWheel" />
      </el-form-item>

      <LongTermMemorySetting
        :enabled="formData.long_term_enable"
        :model-options="llmModelOptions"
        :provider-options="providerOptions"
        :setting="longTermSetting"
        @update:enabled="updateLongTermEnabled"
        @update:setting="updateLongTermSetting"
      />

      <FileUploadSetting
        :enabled="formData.file_upload_enable"
        :setting="formData.file_upload_setting"
        @update:enabled="updateFileUploadEnabled"
        @update:setting="updateFileUploadSetting"
      />

      <UserInput
        :api-fields="apiInputFields"
        :fields="userInputFields"
        :node-id="model.id"
        :setting="userInputSetting"
        @update:fields="updateUserInputFields"
        @update:setting="updateUserInputSetting"
      />

      <ApiParameter :fields="apiInputFields" :user-fields="userInputFields" @update:fields="updateApiInputFields" />

      <ConversationVariable :fields="conversationVariables" @update:fields="updateConversationVariables" />

      <SpeechInput :model-options="sttModelOptions" :provider-options="providerOptions" :setting="speechInputSetting" @update="updateSpeechInput" />

      <SpeechPlayback
        :model-options="ttsModelOptions"
        :provider-options="providerOptions"
        :setting="speechPlaybackSetting"
        @update="updateSpeechPlayback"
      />
    </el-form>
  </NodeContainer>
</template>

<style lang="scss" scoped>
:deep(.el-form-item__label) {
  width: 100%;
}
</style>
