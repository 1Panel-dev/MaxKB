<script setup lang="ts">
import { computed, inject, onMounted, provide, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import { useI18n } from 'vue-i18n'
import type { ModelItem, ModelProviderItem } from '@/api/types'
import type { FormField } from '@/components/mk-dynamics-form'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import type { FormInstance } from 'element-plus'
import SelectModel from '@/components/business/select-model/index.vue'
import { START_NODE_REFERENCES } from '@/workflow-canvas/config/constants'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import { handleNodeWheel } from '@/workflow-canvas/core/utils'
import { useWorkflowStore } from '@/workflow-canvas/store'
import FileUploadSetting from './component/FileUploadSetting.vue'
import LongTermSetting from './component/LongTermSetting.vue'
import ApiParameterTable from './component/api-parameter/ApiParameterTable.vue'
import ConversationVariableTable from './component/conversation-variable/ConversationVariableTable.vue'
import UserInputTable from './component/user-input/UserInputTable.vue'
import { defaultFileUploadSetting } from './constant'
import {
  type ApiInputField,
  type BaseNodeForm,
  type ChatInputField,
  type FileUploadSettingData,
  type LongTermSetting as LongTermSettingData,
  type UserInputSetting,
} from './types'

const { t } = useI18n({ useScope: 'global' })

defineOptions({ name: 'WorkflowBaseNode' })

const getModel = inject('getModel') as () => WorkflowNodeModel
const resourceScope = (inject('resourceScope') as string) || 'workspace'

const model = getModel()
const store = useWorkflowStore(resourceScope)

// 为画布节点中的 ModelSelect 提供参数表单接口。
provide('getModelParamsForm', store.force.getModelParamsForm)
provide('getSelectModelList', store.force.getModelListWithShared)

const formRef = useTemplateRef<FormInstance>('formRef')

// 基本信息与节点数据初始化
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
  prologue: t('application.prologue.defaultValue'),
  stt_autosend: false,
  stt_model_enable: false,
  stt_model_id: '',
  stt_model_params_setting: {},
  stt_model_id_type: 'default',
  tts_autoplay: false,
  tts_model_enable: false,
  tts_model_id: '',
  tts_model_params_setting: {},
  tts_type: 'BROWSER',
}

// 节点初始化时补齐默认值和兼容旧数据，避免读取表单时改写响应式依赖。
const savedForm = cloneDeep(model.properties.node_data) as Partial<BaseNodeForm> | undefined
const savedTtsType = savedForm?.tts_type as string | undefined
model.properties.node_data = {
  ...cloneDeep(defaultForm),
  ...savedForm,
  file_upload_setting: { ...cloneDeep(defaultFileUploadSetting), ...(savedForm?.file_upload_setting ?? {}) },
  long_term_model_id_type: savedForm?.long_term_model_id_type || 'default',
  long_term_model_params_setting: savedForm?.long_term_model_params_setting ?? {},
  long_term_trigger_setting: savedForm?.long_term_trigger_setting ?? { rounds: 10 },
  stt_model_id_type: savedForm?.stt_model_id_type || 'default',
  stt_model_params_setting: savedForm?.stt_model_params_setting ?? {},
  tts_model_params_setting: savedForm?.tts_model_params_setting ?? {},
  tts_type: savedTtsType === 'TTS' ? 'CUSTOM' : savedForm?.tts_type || 'BROWSER',
}

const formData = computed<BaseNodeForm>({
  get: () => model.properties.node_data as BaseNodeForm,
  set: (value) => (model.properties.node_data = value),
})

// 长期记忆
const longTermModelOptions = ref<ModelItem[]>([])
const defaultLongTermModelSetting = computed(() => model.getDefaultModelConfig('LLM'))
const longTermSetting = computed<LongTermSettingData>({
  get: () => ({
    long_term_model_id: formData.value.long_term_model_id,
    long_term_model_id_type: formData.value.long_term_model_id_type,
    long_term_model_params_setting: formData.value.long_term_model_params_setting,
    long_term_trigger_setting: formData.value.long_term_trigger_setting,
    long_term_trigger_type: formData.value.long_term_trigger_type,
  }),
  set: (setting) => {
    Object.assign(formData.value, cloneDeep(setting))
  },
})

function changeLongTermEnabled(enabled: boolean | number | string) {
  formData.value.long_term_enable = Boolean(enabled)
  if (enabled && !formData.value.long_term_model_id_type) formData.value.long_term_model_id_type = 'default'
  model.graphModel.eventCenter.emit('refreshLongTermConfig', undefined)
}

// 文件上传
const fileUploadSetting = computed<FileUploadSettingData>({
  get: () => formData.value.file_upload_setting,
  set: (setting) => {
    formData.value.file_upload_setting = cloneDeep(setting)
    model.graphModel.eventCenter.emit('refreshFileUploadConfig', undefined)
  },
})

function changeFileUploadEnabled(enabled: boolean | number | string) {
  formData.value.file_upload_enable = Boolean(enabled)
  if (enabled && !formData.value.file_upload_setting) {
    formData.value.file_upload_setting = cloneDeep(defaultFileUploadSetting)
  }
  model.graphModel.eventCenter.emit('refreshFileUploadConfig', undefined)
}

// 用户输入：字段、展示设置与显隐引用校验
const userInputFields = computed({
  get: () => (model.properties.user_input_field_list ?? []) as FormField[],
  set: (fields) => {
    model.properties.user_input_field_list = cloneDeep(fields)
    model.graphModel.eventCenter.emit('refreshFieldList', undefined)
  },
})
const userInputSetting = computed<UserInputSetting>({
  get: () =>
    cloneDeep(
      (model.properties.user_input_field_list_setting as UserInputSetting | undefined) ?? {
        exposed_fields: [],
        menu_title: t('workflow.userInput.title'),
      },
    ),
  set: (setting) => {
    model.properties.user_input_field_list_setting = cloneDeep(setting)
  },
})

function validateUserFieldReferences() {
  for (const userField of userInputFields.value) {
    for (const condition of userField.visibility_rules?.conditions ?? []) {
      if (!condition.field?.[0] || !condition.field?.[1]) continue
      const isCurrentForm = condition.field[0] === model.id || (model.id === 'base-node' && condition.field[0] === 'global')
      if (isCurrentForm && !userInputFields.value.some(({ field }) => field === condition.field[1])) {
        return Promise.reject(t('workflow.referenceVariable.missingMessage'))
      }
    }
  }
  return Promise.resolve()
}

// 接口传参
const apiInputFields = computed({
  get: () => (model.properties.api_input_field_list ?? []) as ApiInputField[],
  set: (fields) => {
    model.properties.api_input_field_list = cloneDeep(fields)
    model.graphModel.eventCenter.emit('refreshFieldList', undefined)
  },
})

// 会话变量
const conversationVariables = computed({
  get: () => (model.properties.chat_input_field_list ?? []) as ChatInputField[],
  set: (fields) => {
    model.properties.chat_input_field_list = cloneDeep(fields)
    model.graphModel.eventCenter.emit('chatFieldList', undefined)
  },
})

// 语音输入
const sttModelOptions = ref<ModelItem[]>([])
const defaultSttModelSetting = computed(() => model.getDefaultModelConfig('STT'))

function changeSpeechInputEnabled(enabled: boolean | number | string) {
  if (!enabled) formData.value.stt_model_id = ''
  if (!formData.value.stt_model_id_type) formData.value.stt_model_id_type = 'default'
}

// 语音播放
const ttsModelOptions = ref<ModelItem[]>([])
const defaultTtsModelSetting = computed(() => model.getDefaultModelConfig('TTS'))

function changeSpeechPlaybackEnabled(enabled: boolean | number | string) {
  if (enabled) return
  formData.value.tts_model_id = ''
  formData.value.tts_type = 'BROWSER'
}

// 语音模型共用的供应商选项
const providerOptions = ref<ModelProviderItem[]>([])

// 节点统一校验
function validate() {
  return Promise.all([validateUserFieldReferences(), formRef.value?.validate()]).catch((error) => Promise.reject({ node: model, errMessage: error }))
}

onMounted(() => {
  model.validate = validate
  if (!Array.isArray(model.properties.user_input_field_list)) model.properties.user_input_field_list = []
  if (!Array.isArray(model.properties.api_input_field_list)) model.properties.api_input_field_list = []
  if (!Array.isArray(model.properties.chat_input_field_list)) model.properties.chat_input_field_list = []
  if (!model.properties.user_input_config) model.properties.user_input_config = { title: t('workflow.userInput.title') }

  store.getModelListWithShared({ model_type: 'STT' }).then((models) => (sttModelOptions.value = models))
  store.getModelListWithShared({ model_type: 'LLM' }).then((models) => (longTermModelOptions.value = models))
  store.getModelListWithShared({ model_type: 'TTS' }).then((models) => (ttsModelOptions.value = models))
  store.getProviderList().then((providers) => (providerOptions.value = providers))
})
</script>

<template>
  <NodeContainer :node-model="model">
    <el-form :validate-on-rule-change="false" ref="formRef" :model="formData" label-position="top" require-asterisk-position="right" @submit.prevent>
      <el-form-item
        :label="t('common.name.label')"
        prop="name"
        :rules="{ whitespace: true, required: true, message: t('application.fields.name.requiredMessage'), trigger: 'blur' }"
      >
        <el-input
          v-model="formData.name"
          maxlength="64"
          :placeholder="t('application.fields.name.placeholder')"
          show-word-limit
          @blur="formData.name = formData.name.trim()"
        />
      </el-form-item>

      <el-form-item :label="t('common.description.label')">
        <el-input
          v-model="formData.desc"
          maxlength="256"
          :placeholder="t('application.fields.description.placeholder')"
          :rows="3"
          show-word-limit
          type="textarea"
        />
      </el-form-item>

      <el-form-item :label="t('application.prologue.label')">
        <MdEditorMagnify v-model="formData.prologue" :title="t('application.prologue.label')" @wheel="handleNodeWheel" />
      </el-form-item>

      <!-- 长期记忆 -->
      <el-form-item
        class="mb-2! mk-hide-asterisk"
        prop="long_term_model_id"
        :rules="{
          required: formData.long_term_enable && formData.long_term_model_id_type === 'custom',
          message: t('application.longTermMemory.model.requiredMessage'),
          trigger: 'change',
        }"
      >
        <template #label>
          <div class="flex-between">
            <span class="flex-align-center gap-1">
              <span :class="formData.long_term_enable ? 'mk-required' : ''">{{ t('application.longTermMemory.label') }}</span>

              <MkTooltip :content="t('application.longTermMemory.description', { memory: START_NODE_REFERENCES.memory })" placement="right">
                <MkIcon name="icon_info_outlined" class="text-N600!" />
              </MkTooltip>
            </span>
            <span class="flex-align-center gap-2">
              <!-- 长期记忆设置 -->
              <LongTermSetting
                v-if="formData.long_term_enable"
                v-model="longTermSetting"
                :model-options="longTermModelOptions"
                :default-model-setting="defaultLongTermModelSetting"
                :provider-options="providerOptions"
              />
              <el-switch :model-value="formData.long_term_enable" size="small" @change="changeLongTermEnabled" />
            </span>
          </div>
        </template>
      </el-form-item>

      <!-- 文件上传 -->
      <el-form-item class="mb-2!">
        <template #label>
          <div class="flex-between w-full">
            <span class="flex-align-center gap-1">
              {{ t('application.fileUpload.label') }}
              <MkTooltip :content="t('application.fileUpload.description')" placement="right">
                <MkIcon name="icon_info_outlined" class="text-N600!" />
              </MkTooltip>
            </span>
            <span class="flex-align-center gap-2">
              <FileUploadSetting v-if="formData.file_upload_enable" v-model="fileUploadSetting" />
              <el-switch :model-value="formData.file_upload_enable" size="small" @change="changeFileUploadEnabled" />
            </span>
          </div>
        </template>
      </el-form-item>

      <!-- 用户输入 -->
      <el-form-item>
        <UserInputTable v-model="userInputFields" v-model:setting="userInputSetting" :api-fields="apiInputFields" :node-id="model.id" />
      </el-form-item>
      <!-- 接口传参 -->
      <el-form-item>
        <ApiParameterTable v-model="apiInputFields" :user-fields="userInputFields" />
      </el-form-item>
      <!-- 会话变量 -->
      <el-form-item>
        <ConversationVariableTable v-model="conversationVariables" />
      </el-form-item>

      <!-- 语音输入 -->
      <div class="flex-between">
        <span :class="formData.stt_model_enable ? 'mk-required' : ''">{{ t('application.speechInput.label') }}</span>
        <span class="flex-align-center gap-3">
          <el-checkbox v-if="formData.stt_model_enable" v-model="formData.stt_autosend">{{ t('application.speechInput.autoSend') }}</el-checkbox>
          <el-switch v-model="formData.stt_model_enable" size="small" @change="changeSpeechInputEnabled" />
        </span>
      </div>
      <el-form-item
        v-if="formData.stt_model_enable"
        class="mt-2"
        prop="stt_model_id"
        :rules="{
          trigger: 'change',
          validator: (_rule: unknown, _value: unknown, callback: (error?: Error) => void) => {
            if (formData.stt_model_id_type === 'custom' && !formData.stt_model_id) {
              callback(new Error(t('application.speechInput.model.requiredMessage')))
              return
            }
            if (formData.stt_model_id_type === 'default' && !defaultSttModelSetting?.model_id) {
              callback(new Error(t('workflow.defaultModel.sttRequiredMessage')))
              return
            }
            callback()
          },
        }"
      >
        <el-radio-group v-model="formData.stt_model_id_type" class="mb-2">
          <el-radio value="default">{{ t('workflow.defaultModel.label') }}</el-radio>
          <el-radio value="custom">{{ t('common.options.custom') }}</el-radio>
        </el-radio-group>
        <SelectModel
          v-if="formData.stt_model_id_type === 'default'"
          :model-value="defaultSttModelSetting?.model_id ?? ''"
          :model-params="defaultSttModelSetting?.model_params_setting ?? {}"
          disabled
          :options="sttModelOptions"
          :provider-options="providerOptions"
          :placeholder="t('workflow.defaultModel.unconfigured')"
        />
        <SelectModel
          v-else
          v-model="formData.stt_model_id"
          v-model:model-params="formData.stt_model_params_setting"
          can-edit-params
          :options="sttModelOptions"
          :provider-options="providerOptions"
        />
      </el-form-item>

      <!-- 语音播放 -->
      <div class="flex-between mt-4">
        <span :class="formData.tts_model_enable && formData.tts_type !== 'BROWSER' ? 'mk-required' : ''">
          {{ t('application.speechPlayback.label') }}
        </span>
        <span class="flex-align-center gap-3">
          <el-checkbox v-if="formData.tts_model_enable" v-model="formData.tts_autoplay">{{ t('application.speechPlayback.autoPlay') }}</el-checkbox>
          <el-switch v-model="formData.tts_model_enable" size="small" @change="changeSpeechPlaybackEnabled" />
        </span>
      </div>

      <el-form-item
        v-if="formData.tts_model_enable"
        class="mt-2"
        prop="tts_model_id"
        :rules="{
          trigger: 'change',
          validator: (_rule: unknown, _value: unknown, callback: (error?: Error) => void) => {
            if (formData.tts_type === 'CUSTOM' && !formData.tts_model_id) {
              callback(new Error(t('application.speechPlayback.model.requiredMessage')))
              return
            }
            if (formData.tts_type === 'DEFAULT' && !defaultTtsModelSetting?.model_id) {
              callback(new Error(t('workflow.defaultModel.ttsRequiredMessage')))
              return
            }
            callback()
          },
        }"
      >
        <el-radio-group v-model="formData.tts_type" class="mb-2">
          <el-radio value="BROWSER">{{ t('application.speechPlayback.browser') }}</el-radio>
          <el-radio value="DEFAULT">{{ t('workflow.defaultModel.label') }}</el-radio>
          <el-radio value="CUSTOM">{{ t('common.options.custom') }}</el-radio>
        </el-radio-group>
        <SelectModel
          v-if="formData.tts_type === 'DEFAULT'"
          :model-value="defaultTtsModelSetting?.model_id ?? ''"
          :model-params="defaultTtsModelSetting?.model_params_setting ?? {}"
          disabled
          :options="ttsModelOptions"
          :provider-options="providerOptions"
          :placeholder="t('workflow.defaultModel.unconfigured')"
        />
        <SelectModel
          v-else-if="formData.tts_type === 'CUSTOM'"
          v-model="formData.tts_model_id"
          v-model:model-params="formData.tts_model_params_setting"
          can-edit-params
          :options="ttsModelOptions"
          :provider-options="providerOptions"
        />
      </el-form-item>
    </el-form>
  </NodeContainer>
</template>
