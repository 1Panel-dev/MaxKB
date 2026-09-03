<script setup lang="ts">
import { computed, inject, onMounted, ref, useTemplateRef } from 'vue'
import { cloneDeep, set } from 'lodash'
import type { FormInstance } from 'element-plus'
import { Operation, QuestionFilled } from '@element-plus/icons-vue'
import ModelSelect from '@/components/business/model-select/index.vue'
import type { ModelItem, ModelProviderItem } from '@/api/types'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import { useWorkflowStore } from '@/workflow-canvas/store'
import BaseNodeFieldTables from './BaseNodeFieldTables.vue'
import FileUploadSettingDialog from './FileUploadSettingDialog.vue'
import LongTermSettingDialog from './LongTermSettingDialog.vue'
import ModelParamsDialog from './ModelParamsDialog.vue'
import PrologueEditor from './PrologueEditor.vue'
import { defaultFileUploadSetting, type BaseNodeForm, type LongTermSetting, type UserInputField } from './types'

defineOptions({ name: 'WorkflowBaseNode' })

const getModel = inject('getModel') as () => WorkflowNodeModel
const apiType = (inject('apiType') as string) || 'workspace'
const model = getModel()
const store = useWorkflowStore(apiType)

const formRef = useTemplateRef<FormInstance>('formRef')
const fileUploadDialogRef = useTemplateRef<InstanceType<typeof FileUploadSettingDialog>>('fileUploadDialogRef')
const longTermDialogRef = useTemplateRef<InstanceType<typeof LongTermSettingDialog>>('longTermDialogRef')
const ttsParamsDialogRef = useTemplateRef<InstanceType<typeof ModelParamsDialog>>('ttsParamsDialogRef')

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

function validateUserFieldReferences() {
  const userFields = (model.properties.user_input_field_list ?? []) as UserInputField[]
  for (const userField of userFields) {
    for (const condition of userField.visibility_rules?.conditions ?? []) {
      if (!condition.field?.[0] || !condition.field?.[1]) continue
      const isCurrentForm = condition.field[0] === model.id || (model.id === 'base-node' && condition.field[0] === 'global')
      if (isCurrentForm && !userFields.some(({ field }) => field === condition.field[1])) return Promise.reject('用户输入参数引用了已删除的变量')
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

function switchLongTermMemory() {
  if (formData.value.long_term_enable && !formData.value.long_term_model_id_type) formData.value.long_term_model_id_type = 'default'
  model.graphModel.eventCenter.emit('refreshLongTermConfig', undefined)
}

function openLongTermSettings() {
  const setting: LongTermSetting = {
    long_term_model_id: formData.value.long_term_model_id,
    long_term_model_id_type: formData.value.long_term_model_id_type,
    long_term_model_params_setting: formData.value.long_term_model_params_setting,
    long_term_trigger_setting: formData.value.long_term_trigger_setting,
    long_term_trigger_type: formData.value.long_term_trigger_type,
  }
  longTermDialogRef.value?.open(setting)
}

function submitLongTermSettings(setting: LongTermSetting) {
  Object.assign(formData.value, setting)
  model.graphModel.eventCenter.emit('refreshLongTermConfig', undefined)
}

function switchFileUpload() {
  if (formData.value.file_upload_enable && !formData.value.file_upload_setting) {
    formData.value.file_upload_setting = cloneDeep(defaultFileUploadSetting)
  }
  model.graphModel.eventCenter.emit('refreshFileUploadConfig', undefined)
}

function submitFileUploadSettings(setting: BaseNodeForm['file_upload_setting']) {
  formData.value.file_upload_setting = setting
  model.graphModel.eventCenter.emit('refreshFileUploadConfig', undefined)
}

function switchSttModel() {
  if (!formData.value.stt_model_enable) formData.value.stt_model_id = ''
  if (!formData.value.stt_model_id_type) formData.value.stt_model_id_type = 'default'
}

function switchTtsModel() {
  if (!formData.value.tts_model_enable) {
    formData.value.tts_model_id = ''
    formData.value.tts_type = 'BROWSER'
  }
}

function changeTtsModel(modelId: string) {
  formData.value.tts_model_id = modelId
  if (!modelId) {
    formData.value.tts_model_params_setting = {}
    return
  }
  ttsParamsDialogRef.value?.resetDefault(modelId).then((settings) => {
    formData.value.tts_model_params_setting = settings
  })
}

function openTtsParams() {
  if (!formData.value.tts_model_id) return
  ttsParamsDialogRef.value?.open(formData.value.tts_model_id, formData.value.tts_model_params_setting)
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
        <PrologueEditor v-model="formData.prologue" />
      </el-form-item>

      <el-form-item>
        <template #label>
          <div class="flex-between w-full">
            <span class="flex items-center gap-1">
              长期记忆
              <el-tooltip content="开启后，智能体会按配置从历史对话中提取长期记忆，可通过 {{开始.memory}} 引用" placement="right">
                <MkIcon :icon="QuestionFilled" class="cursor-help text-N600" />
              </el-tooltip>
            </span>
            <span class="flex items-center gap-2">
              <el-button v-if="formData.long_term_enable" link type="primary" title="长期记忆设置" @click="openLongTermSettings">
                <MkIcon :icon="Operation" />
              </el-button>
              <el-switch v-model="formData.long_term_enable" size="small" @change="switchLongTermMemory" />
            </span>
          </div>
        </template>
        <el-text v-if="formData.long_term_enable" type="info">长期记忆使用默认模型或设置中选择的自定义模型。</el-text>
      </el-form-item>

      <el-form-item>
        <template #label>
          <div class="flex-between w-full">
            <span class="flex items-center gap-1">
              文件上传
              <el-tooltip content="允许用户在对话中上传文件，并限制文件数量、大小、类型和上传方式" placement="right">
                <MkIcon :icon="QuestionFilled" class="cursor-help text-N600" />
              </el-tooltip>
            </span>
            <span class="flex items-center gap-2">
              <el-button
                v-if="formData.file_upload_enable"
                link
                type="primary"
                title="文件上传设置"
                @click="fileUploadDialogRef?.open(formData.file_upload_setting)"
              >
                <MkIcon :icon="Operation" />
              </el-button>
              <el-switch v-model="formData.file_upload_enable" size="small" @change="switchFileUpload" />
            </span>
          </div>
        </template>
      </el-form-item>

      <BaseNodeFieldTables :node-model="model" />

      <el-form-item>
        <template #label>
          <div class="flex-between w-full">
            <span>语音输入</span>
            <span class="flex items-center gap-3">
              <el-checkbox v-if="formData.stt_model_enable" v-model="formData.stt_autosend">识别后自动发送</el-checkbox>
              <el-switch v-model="formData.stt_model_enable" size="small" @change="switchSttModel" />
            </span>
          </div>
        </template>
        <template v-if="formData.stt_model_enable">
          <el-radio-group v-model="formData.stt_model_id_type" class="mb-2">
            <el-radio value="default">默认模型</el-radio>
            <el-radio value="custom">自定义</el-radio>
          </el-radio-group>
          <el-alert v-if="formData.stt_model_id_type === 'default'" class="w-full" title="使用系统默认语音识别模型" type="info" :closable="false" />
          <ModelSelect
            v-else
            v-model="formData.stt_model_id"
            :options="sttModelOptions"
            :provider-options="providerOptions"
            placeholder="请选择语音识别模型"
          />
        </template>
      </el-form-item>

      <el-form-item>
        <template #label>
          <div class="flex-between w-full">
            <span>语音播放</span>
            <span class="flex items-center gap-3">
              <el-checkbox v-if="formData.tts_model_enable" v-model="formData.tts_autoplay">自动播放</el-checkbox>
              <el-switch v-model="formData.tts_model_enable" size="small" @change="switchTtsModel" />
            </span>
          </div>
        </template>
        <template v-if="formData.tts_model_enable">
          <el-radio-group v-model="formData.tts_type" class="mb-2">
            <el-radio value="BROWSER">浏览器</el-radio>
            <el-radio value="DEFAULT">默认模型</el-radio>
            <el-radio value="CUSTOM">自定义</el-radio>
          </el-radio-group>
          <el-alert v-if="formData.tts_type === 'BROWSER'" class="w-full" title="使用浏览器内置语音播放" type="info" :closable="false" />
          <el-alert v-else-if="formData.tts_type === 'DEFAULT'" class="w-full" title="使用系统默认语音合成模型" type="info" :closable="false" />
          <div v-else class="flex w-full gap-2">
            <ModelSelect
              v-model="formData.tts_model_id"
              :options="ttsModelOptions"
              :provider-options="providerOptions"
              placeholder="请选择语音合成模型"
              @change="changeTtsModel"
            />
            <el-button :disabled="!formData.tts_model_id" title="模型参数设置" @click="openTtsParams">
              <MkIcon :icon="Operation" />
            </el-button>
          </div>
        </template>
      </el-form-item>
    </el-form>

    <FileUploadSettingDialog ref="fileUploadDialogRef" @submit="submitFileUploadSettings" />
    <LongTermSettingDialog
      ref="longTermDialogRef"
      :model-options="llmModelOptions"
      :provider-options="providerOptions"
      @submit="submitLongTermSettings"
    />
    <ModelParamsDialog ref="ttsParamsDialogRef" @submit="formData.tts_model_params_setting = $event" />
  </NodeContainer>
</template>

<style lang="scss" scoped>
:deep(.el-form-item__label) {
  width: 100%;
}
</style>
