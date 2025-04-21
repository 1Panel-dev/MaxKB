<template>
  <NodeContainer :nodeModel="nodeModel">
    <el-form
      @submit.prevent
      :model="form_data"
      label-position="top"
      require-asterisk-position="right"
      class="mb-24"
      label-width="auto"
      ref="baseNodeFormRef"
    >
      <el-form-item
        :label="$t('views.applicationWorkflow.nodes.baseNode.appName.label')"
        prop="name"
        :rules="{
          message: t('views.application.applicationForm.form.appName.requiredMessage'),
          trigger: 'blur',
          required: true
        }"
      >
        <el-input
          v-model="form_data.name"
          maxlength="64"
          :placeholder="t('views.application.applicationForm.form.appName.placeholder')"
          show-word-limit
          @blur="form_data.name = form_data.name?.trim()"
        />
      </el-form-item>
      <el-form-item :label="$t('views.applicationWorkflow.nodes.baseNode.appDescription.label')">
        <el-input
          v-model="form_data.desc"
          :placeholder="$t('views.application.applicationForm.form.appDescription.placeholder')"
          :rows="3"
          type="textarea"
          maxlength="256"
          show-word-limit
        />
      </el-form-item>
      <el-form-item :label="$t('views.application.applicationForm.form.prologue')">
        <MdEditorMagnify
          @wheel="wheel"
          :title="$t('views.application.applicationForm.form.prologue')"
          v-model="form_data.prologue"
          style="height: 150px"
          @submitDialog="submitDialog"
        />
      </el-form-item>
      <el-form-item>
        <template #label>
          <div class="flex-between">
            <div class="flex align-center">
              <span class="mr-4">{{
                $t('views.applicationWorkflow.nodes.baseNode.fileUpload.label')
              }}</span>
              <el-tooltip
                effect="dark"
                :content="$t('views.applicationWorkflow.nodes.baseNode.fileUpload.tooltip')"
                placement="right"
              >
                <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
              </el-tooltip>
            </div>
            <div>
              <el-button
                v-if="form_data.file_upload_enable"
                type="primary"
                link
                @click="openFileUploadSettingDialog"
                class="mr-4"
              >
                <el-icon class="mr-4">
                  <Setting />
                </el-icon>
              </el-button>
              <el-switch
                size="small"
                v-model="form_data.file_upload_enable"
                @change="switchFileUpload"
              />
            </div>
          </div>
        </template>
      </el-form-item>
      <UserInputFieldTable ref="UserInputFieldTableFef" :node-model="nodeModel" />
      <ApiInputFieldTable ref="ApiInputFieldTableFef" :node-model="nodeModel" />
      <el-form-item>
        <template #label>
          <div class="flex-between">
            <span class="mr-4">{{
              $t('views.application.applicationForm.form.voiceInput.label')
            }}</span>
            <div class="flex">
              <el-checkbox v-if="form_data.stt_model_enable" v-model="form_data.stt_autosend">{{
                $t('views.application.applicationForm.form.voiceInput.autoSend')
              }}</el-checkbox>
              <el-switch
                class="ml-8"
                size="small"
                v-model="form_data.stt_model_enable"
                @change="sttModelEnableChange"
              />
            </div>
          </div>
        </template>
        <ModelSelect
          @wheel="wheel"
          v-show="form_data.stt_model_enable"
          v-model="form_data.stt_model_id"
          :placeholder="$t('views.application.applicationForm.form.voiceInput.placeholder')"
          :options="sttModelOptions"
          showFooter
          :model-type="'STT'"
        ></ModelSelect>
      </el-form-item>
      <el-form-item>
        <template #label>
          <div class="flex-between">
            <span class="mr-4">{{
              $t('views.application.applicationForm.form.voicePlay.label')
            }}</span>
            <div class="flex">
              <el-checkbox v-if="form_data.tts_model_enable" v-model="form_data.tts_autoplay">{{
                $t('views.application.applicationForm.form.voicePlay.autoPlay')
              }}</el-checkbox>
              <el-switch
                class="ml-8"
                size="small"
                v-model="form_data.tts_model_enable"
                @change="ttsModelEnableChange"
              />
            </div>
          </div>
        </template>
        <div class="w-full">
          <el-radio-group v-model="form_data.tts_type" v-show="form_data.tts_model_enable">
            <el-radio
              :label="$t('views.application.applicationForm.form.voicePlay.browser')"
              value="BROWSER"
            />
            <el-radio
              :label="$t('views.application.applicationForm.form.voicePlay.tts')"
              value="TTS"
            />
          </el-radio-group>
        </div>
        <div class="flex-between w-full">
          <ModelSelect
            @wheel="wheel"
            v-if="form_data.tts_type === 'TTS' && form_data.tts_model_enable"
            v-model="form_data.tts_model_id"
            :placeholder="$t('views.application.applicationForm.form.voicePlay.placeholder')"
            :options="ttsModelOptions"
            @change="ttsModelChange()"
            showFooter
            :model-type="'TTS'"
          ></ModelSelect>

          <el-button
            v-if="form_data.tts_type === 'TTS' && form_data.tts_model_enable"
            @click="openTTSParamSettingDialog"
            :disabled="!form_data.tts_model_id"
            class="ml-8"
          >
            <el-icon>
              <el-icon><Operation /></el-icon>
            </el-icon>
          </el-button>
        </div>
      </el-form-item>
    </el-form>
    <TTSModeParamSettingDialog ref="TTSModeParamSettingDialogRef" @refresh="refreshTTSForm" />
    <FileUploadSettingDialog
      ref="FileUploadSettingDialogRef"
      :node-model="nodeModel"
      @refresh="refreshFileUploadForm"
    />
  </NodeContainer>
</template>
<script setup lang="ts">
import { app } from '@/main'
import { groupBy, set } from 'lodash'
import NodeContainer from '@/workflow/common/NodeContainer.vue'
import type { FormInstance } from 'element-plus'
import { ref, computed, onMounted } from 'vue'
import applicationApi from '@/api/application'
import { MsgError, MsgSuccess, MsgWarning } from '@/utils/message'
import { t } from '@/locales'
import TTSModeParamSettingDialog from '@/views/application/component/TTSModeParamSettingDialog.vue'
import ApiInputFieldTable from './component/ApiInputFieldTable.vue'
import UserInputFieldTable from './component/UserInputFieldTable.vue'
import FileUploadSettingDialog from '@/workflow/nodes/base-node/component/FileUploadSettingDialog.vue'

const {
  params: { id }
} = app.config.globalProperties.$route as any

const props = defineProps<{ nodeModel: any }>()

const sttModelOptions = ref<any>(null)
const ttsModelOptions = ref<any>(null)
const TTSModeParamSettingDialogRef = ref<InstanceType<typeof TTSModeParamSettingDialog>>()
const UserInputFieldTableFef = ref()
const ApiInputFieldTableFef = ref()
const FileUploadSettingDialogRef = ref<InstanceType<typeof FileUploadSettingDialog>>()

const form = {
  name: '',
  desc: '',
  prologue: t('views.application.applicationForm.form.defaultPrologue')
}

const wheel = (e: any) => {
  if (e.ctrlKey === true) {
    e.preventDefault()
    return true
  } else {
    e.stopPropagation()
    return true
  }
}

function submitDialog(val: string) {
  set(props.nodeModel.properties.node_data, 'prologue', val)
}

const form_data = computed({
  get: () => {
    if (props.nodeModel.properties.node_data) {
      return props.nodeModel.properties.node_data
    } else {
      set(props.nodeModel.properties, 'node_data', form)
    }
    return props.nodeModel.properties.node_data
  },
  set: (value) => {
    set(props.nodeModel.properties, 'node_data', value)
  }
})

const baseNodeFormRef = ref<FormInstance>()

const validate = () => {
  if (
    form_data.value.tts_model_enable &&
    !form_data.value.tts_model_id &&
    form_data.value.tts_type === 'TTS'
  ) {
    return Promise.reject({
      node: props.nodeModel,
      errMessage: t('views.application.applicationForm.form.voicePlay.requiredMessage')
    })
  }
  if (form_data.value.stt_model_enable && !form_data.value.stt_model_id) {
    return Promise.reject({
      node: props.nodeModel,
      errMessage: t('views.application.applicationForm.form.voiceInput.requiredMessage')
    })
  }
  return baseNodeFormRef.value?.validate().catch((err) => {
    return Promise.reject({ node: props.nodeModel, errMessage: err })
  })
}

function getSTTModel() {
  applicationApi.getApplicationSTTModel(id).then((res: any) => {
    sttModelOptions.value = groupBy(res?.data, 'provider')
  })
}

function getTTSModel() {
  applicationApi.getApplicationTTSModel(id).then((res: any) => {
    ttsModelOptions.value = groupBy(res?.data, 'provider')
  })
}

function ttsModelChange() {
  if (form_data.value.tts_model_id) {
    TTSModeParamSettingDialogRef.value?.reset_default(form_data.value.tts_model_id, id)
  } else {
    refreshTTSForm({})
  }
}

function ttsModelEnableChange() {
  if (!form_data.value.tts_model_enable) {
    form_data.value.tts_model_id = ''
    form_data.value.tts_type = 'BROWSER'
  }
}

function sttModelEnableChange() {
  if (!form_data.value.stt_model_enable) {
    form_data.value.stt_model_id = ''
  }
}

const openTTSParamSettingDialog = () => {
  const model_id = form_data.value.tts_model_id
  if (!model_id) {
    MsgSuccess(t('views.application.applicationForm.form.voicePlay.requiredMessage'))
    return
  }
  TTSModeParamSettingDialogRef.value?.open(model_id, id, form_data.value.tts_model_params_setting)
}

const refreshTTSForm = (data: any) => {
  form_data.value.tts_model_params_setting = data
}

const switchFileUpload = () => {
  const default_upload_setting = {
    maxFiles: 3,
    fileLimit: 50,
    document: true,
    image: false,
    audio: false,
    video: false,
    other: false,
    otherExtensions: ['ppt', 'doc']
  }

  if (form_data.value.file_upload_enable) {
    form_data.value.file_upload_setting =
      form_data.value.file_upload_setting || default_upload_setting
  }
  props.nodeModel.graphModel.eventCenter.emit('refreshFileUploadConfig')
}
const openFileUploadSettingDialog = () => {
  FileUploadSettingDialogRef.value?.open(form_data.value.file_upload_setting)
}

const refreshFileUploadForm = (data: any) => {
  form_data.value.file_upload_setting = data
}

onMounted(() => {
  set(props.nodeModel, 'validate', validate)
  if (!props.nodeModel.properties.node_data.tts_type) {
    set(props.nodeModel.properties.node_data, 'tts_type', 'BROWSER')
  }
  getTTSModel()
  getSTTModel()
})
</script>
<style lang="scss" scoped>
:deep(.el-form-item__label) {
  display: block;
}
</style>
