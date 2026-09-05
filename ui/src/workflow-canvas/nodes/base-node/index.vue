<script setup lang="ts">
import { computed, inject, onMounted, ref, useTemplateRef } from 'vue'
import { cloneDeep } from 'lodash'
import type { FormInstance } from 'element-plus'
import type { ModelItem, ModelProviderItem } from '@/api/types'
import ModelSelect from '@/components/business/model-select/index.vue'
import type { FormField } from '@/components/mk-dynamics-form'
import NodeContainer from '@/workflow-canvas/core/node-container/index.vue'
import type { WorkflowNodeModel } from '@/workflow-canvas/core/workflow-node'
import { useWorkflowStore } from '@/workflow-canvas/store'
import ApiParameter from './component/api-parameter/index.vue'
import ConversationVariable from './component/conversation-variable/index.vue'
import UserInput from './component/user-input/index.vue'
import { defaultFileUploadSetting } from './constant'
import { type ApiInputField, type BaseNodeForm, type ChatInputField, type UserInputSetting } from './types'

defineOptions({ name: 'WorkflowBaseNode' })

const getModel = inject('getModel') as () => WorkflowNodeModel
const apiType = (inject('apiType') as string) || 'workspace'
const model = getModel()
const store = useWorkflowStore(apiType)

const formRef = useTemplateRef<FormInstance>('formRef')

const sttModelOptions = ref<ModelItem[]>([])
const ttsModelOptions = ref<ModelItem[]>([])
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

function handleEditorWheel(event: WheelEvent) {
  if (event.ctrlKey) event.preventDefault()
  else event.stopPropagation()
}

// 子模块数据映射
const userInputFields = computed(() => (model.properties.user_input_field_list ?? []) as FormField[])
const apiInputFields = computed(() => (model.properties.api_input_field_list ?? []) as ApiInputField[])
const conversationVariables = computed(() => (model.properties.chat_input_field_list ?? []) as ChatInputField[])
const userInputSetting = computed<UserInputSetting>(() =>
  cloneDeep((model.properties.user_input_field_list_setting as UserInputSetting | undefined) ?? { exposed_fields: [], menu_title: '更多设置' }),
)
const defaultSttModelSetting = computed(() => model.getDefaultModelConfig('STT'))
const defaultTtsModelSetting = computed(() => model.getDefaultModelConfig('TTS'))

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
  if (formData.value.tts_model_enable && formData.value.tts_type === 'DEFAULT' && !defaultTtsModelSetting.value?.model_id) {
    return Promise.reject({ node: model, errMessage: '请在默认模型设置中选择语音合成模型' })
  }
  if (formData.value.stt_model_enable && formData.value.stt_model_id_type === 'custom' && !formData.value.stt_model_id) {
    return Promise.reject({ node: model, errMessage: '请选择语音输入模型' })
  }
  if (formData.value.stt_model_enable && formData.value.stt_model_id_type === 'default' && !defaultSttModelSetting.value?.model_id) {
    return Promise.reject({ node: model, errMessage: '请在默认模型设置中选择语音识别模型' })
  }
  if (formData.value.long_term_enable && formData.value.long_term_model_id_type === 'custom' && !formData.value.long_term_model_id) {
    return Promise.reject({ node: model, errMessage: '请选择长期记忆模型' })
  }
  return Promise.all([validateUserFieldReferences(), formRef.value?.validate()]).catch((error) => Promise.reject({ node: model, errMessage: error }))
}

// 子模块数据更新
function changeLongTermEnabled(enabled: boolean | number | string) {
  formData.value.long_term_enable = Boolean(enabled)
  if (enabled && !formData.value.long_term_model_id_type) formData.value.long_term_model_id_type = 'default'
  model.graphModel.eventCenter.emit('refreshLongTermConfig', undefined)
}

function changeFileUploadEnabled(enabled: boolean | number | string) {
  formData.value.file_upload_enable = Boolean(enabled)
  if (enabled && !formData.value.file_upload_setting) {
    formData.value.file_upload_setting = cloneDeep(defaultFileUploadSetting)
  }
  model.graphModel.eventCenter.emit('refreshFileUploadConfig', undefined)
}

function updateUserInputFields(fields: FormField[]) {
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

function changeSpeechInputEnabled(enabled: boolean | number | string) {
  if (!enabled) formData.value.stt_model_id = ''
  if (!formData.value.stt_model_id_type) formData.value.stt_model_id_type = 'default'
}

function changeSpeechPlaybackEnabled(enabled: boolean | number | string) {
  if (enabled) return
  formData.value.tts_model_id = ''
  formData.value.tts_type = 'BROWSER'
}

onMounted(() => {
  model.validate = validate
  if (!Array.isArray(model.properties.user_input_field_list)) model.properties.user_input_field_list = []
  if (!Array.isArray(model.properties.api_input_field_list)) model.properties.api_input_field_list = []
  if (!Array.isArray(model.properties.chat_input_field_list)) model.properties.chat_input_field_list = []
  if (!model.properties.user_input_config) model.properties.user_input_config = { title: '用户输入' }

  store.getModelList({ model_type: 'STT' }).then((models) => (sttModelOptions.value = models))
  store.getModelList({ model_type: 'TTS' }).then((models) => (ttsModelOptions.value = models))
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
        <MdEditorMagnify v-model="formData.prologue" title="开场白" @wheel="handleEditorWheel" />
      </el-form-item>

      <!-- 长期记忆 -->
      <div class="mb-4 flex-between">
        <span class="flex items-center gap-1">
          长期记忆
          <el-tooltip
            content="开启后，从开启时间记录新对话并按周期生成记忆，可通过 {{开始.memory}} 变量在系统提示词中调用。关闭后，将清空对话用户的长期记忆，再次开启将重新从开启时点开始累积。"
            placement="right"
          >
            <MkIcon name="icon_info_outlined" class="text-N600!" />
          </el-tooltip>
        </span>
        <span class="flex items-center gap-2">
          <!-- // TODO 长期记忆设置 -->
          <el-button v-if="formData.long_term_enable" text type="primary">
            <MkIcon name="icon-setting" />
          </el-button>
          <el-switch :model-value="formData.long_term_enable" size="small" @change="changeLongTermEnabled" />
        </span>
      </div>

      <div class="mb-4 flex-between w-full">
        <span class="flex items-center gap-1">
          文件上传
          <el-tooltip content="开启后，问答页面会显示上传文件的按钮。" placement="right">
            <MkIcon name="icon_info_outlined" class="text-N600!" />
          </el-tooltip>
        </span>
        <span class="flex items-center gap-2">
          <!-- // TODO 文件上传设置 -->
          <el-button v-if="formData.file_upload_enable" text type="primary">
            <MkIcon name="icon-setting" />
          </el-button>
          <el-switch :model-value="formData.file_upload_enable" size="small" @change="changeFileUploadEnabled" />
        </span>
      </div>

      <!-- 用户输入 TODO 整理 -->
      <UserInput
        :api-fields="apiInputFields"
        :fields="userInputFields"
        :node-id="model.id"
        :setting="userInputSetting"
        @update:fields="updateUserInputFields"
        @update:setting="updateUserInputSetting"
      />
      <!-- 接口传参 TODO 整理 -->
      <ApiParameter :fields="apiInputFields" :user-fields="userInputFields" @update:fields="updateApiInputFields" />

      <!-- 会话变量 TODO 整理 -->
      <ConversationVariable :fields="conversationVariables" @update:fields="updateConversationVariables" />

      <!-- 语音输入 -->
      <div class="flex-between mb-2">
        <span>语音输入</span>
        <span class="flex items-center gap-3">
          <el-checkbox v-if="formData.stt_model_enable" v-model="formData.stt_autosend">自动发送</el-checkbox>
          <el-switch v-model="formData.stt_model_enable" size="small" @change="changeSpeechInputEnabled" />
        </span>
      </div>
      <el-form-item>
        <template v-if="formData.stt_model_enable">
          <el-radio-group v-model="formData.stt_model_id_type" class="mb-2">
            <el-radio value="default">默认模型</el-radio>
            <el-radio value="custom">自定义</el-radio>
          </el-radio-group>
          <ModelSelect
            v-if="formData.stt_model_id_type === 'default'"
            :model-value="defaultSttModelSetting?.model_id ?? ''"
            :model-params="defaultSttModelSetting?.model_params_setting ?? {}"
            disabled
            :options="sttModelOptions"
            :provider-options="providerOptions"
            placeholder="未配置默认模型"
          />
          <ModelSelect
            v-else
            v-model="formData.stt_model_id"
            v-model:model-params="formData.stt_model_params_setting"
            can-edit-params
            :options="sttModelOptions"
            :provider-options="providerOptions"
          />
        </template>
      </el-form-item>

      <!-- 语音播放 -->
      <div class="flex-between mb-2">
        <span>语音播放</span>
        <span class="flex items-center gap-3">
          <el-checkbox v-if="formData.tts_model_enable" v-model="formData.tts_autoplay">自动播放</el-checkbox>
          <el-switch v-model="formData.tts_model_enable" size="small" @change="changeSpeechPlaybackEnabled" />
        </span>
      </div>

      <el-form-item class="mb-0!">
        <template v-if="formData.tts_model_enable">
          <el-radio-group v-model="formData.tts_type" class="mb-2">
            <el-radio value="BROWSER">浏览器播放(免费)</el-radio>
            <el-radio value="DEFAULT">默认模型</el-radio>
            <el-radio value="CUSTOM">自定义</el-radio>
          </el-radio-group>
          <ModelSelect
            v-if="formData.tts_type === 'DEFAULT'"
            :model-value="defaultTtsModelSetting?.model_id ?? ''"
            :model-params="defaultTtsModelSetting?.model_params_setting ?? {}"
            disabled
            :options="ttsModelOptions"
            :provider-options="providerOptions"
            placeholder="未配置默认模型"
          />
          <ModelSelect
            v-else-if="formData.tts_type === 'CUSTOM'"
            v-model="formData.tts_model_id"
            v-model:model-params="formData.tts_model_params_setting"
            can-edit-params
            :options="ttsModelOptions"
            :provider-options="providerOptions"
          />
        </template>
      </el-form-item>
    </el-form>
  </NodeContainer>
</template>
