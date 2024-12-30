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
        label="应用名称"
        prop="name"
        :rules="{
          message: '应用名称不能为空',
          trigger: 'blur',
          required: true
        }"
      >
        <el-input
          v-model="form_data.name"
          maxlength="64"
          placeholder="请输入应用名称"
          show-word-limit
          @blur="form_data.name = form_data.name?.trim()"
        />
      </el-form-item>
      <el-form-item label="应用描述">
        <el-input
          v-model="form_data.desc"
          placeholder="请输入应用描述"
          :rows="3"
          type="textarea"
          maxlength="256"
          show-word-limit
        />
      </el-form-item>
      <el-form-item label="开场白">
        <MdEditorMagnify
          @wheel="wheel"
          title="开场白"
          v-model="form_data.prologue"
          style="height: 150px"
          @submitDialog="submitDialog"
        />
      </el-form-item>
      <el-form-item>
        <template #label>
          <div class="flex-between">
            <div class="flex align-center">
              <span class="mr-4">文件上传</span>
              <el-tooltip
                effect="dark"
                content="开启后，问答页面会显示上传文件的按钮。"
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
            <div class="flex align-center">
              <span class="mr-4">语音输入</span>
              <!-- <el-tooltip
                effect="dark"
                content="开启后，需要设定语音转文本模型，语音输入完成后会转化为文字直接发送提问"
                placement="right"
              >
                <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
              </el-tooltip> -->
            </div>
            <el-switch
              size="small"
              v-model="form_data.stt_model_enable"
              @change="sttModelEnableChange"
            />
          </div>
        </template>

        <el-select
          v-show="form_data.stt_model_enable"
          v-model="form_data.stt_model_id"
          class="w-full"
          @wheel="wheel"
          popper-class="select-model"
          placeholder="请选择语音识别模型"
        >
          <el-option-group
            v-for="(value, label) in sttModelOptions"
            :key="value"
            :label="relatedObject(providerOptions, label, 'provider')?.name"
          >
            <el-option
              v-for="item in value.filter((v: any) => v.status === 'SUCCESS')"
              :key="item.id"
              :label="item.name"
              :value="item.id"
              class="flex-between"
            >
              <div class="flex align-center">
                <span
                  v-html="relatedObject(providerOptions, label, 'provider')?.icon"
                  class="model-icon mr-8"
                ></span>
                <span>{{ item.name }}</span>
                <el-tag v-if="item.permission_type === 'PUBLIC'" type="info" class="info-tag ml-8"
                  >公用
                </el-tag>
              </div>
              <el-icon class="check-icon" v-if="item.id === form_data.stt_model_id">
                <Check />
              </el-icon>
            </el-option>
            <!-- 不可用 -->
            <el-option
              v-for="item in value.filter((v: any) => v.status !== 'SUCCESS')"
              :key="item.id"
              :label="item.name"
              :value="item.id"
              class="flex-between"
              disabled
            >
              <div class="flex">
                <span
                  v-html="relatedObject(providerOptions, label, 'provider')?.icon"
                  class="model-icon mr-8"
                ></span>
                <span>{{ item.name }}</span>
                <span class="danger">{{
                  $t('views.application.applicationForm.form.aiModel.unavailable')
                }}</span>
              </div>
              <el-icon class="check-icon" v-if="item.id === form_data.stt_model_id">
                <Check />
              </el-icon>
            </el-option>
          </el-option-group>
        </el-select>
      </el-form-item>
      <el-form-item>
        <template #label>
          <div class="flex-between">
            <span class="mr-4">语音播放</span>
            <div>
              <el-button
                v-if="form_data.tts_type === 'TTS' && form_data.tts_model_enable"
                type="primary"
                link
                @click="openTTSParamSettingDialog"
                :disabled="!form_data.tts_model_id"
                class="mr-4"
              >
                <el-icon class="mr-4">
                  <Setting />
                </el-icon>
              </el-button>
              <el-switch
                size="small"
                v-model="form_data.tts_model_enable"
                @change="ttsModelEnableChange"
              />
            </div>
          </div>
        </template>
        <el-radio-group v-model="form_data.tts_type" v-show="form_data.tts_model_enable">
          <el-radio label="浏览器播放(免费)" value="BROWSER" />
          <el-radio label="TTS模型" value="TTS" />
        </el-radio-group>
        <el-select
          v-if="form_data.tts_type === 'TTS' && form_data.tts_model_enable"
          v-model="form_data.tts_model_id"
          class="w-full"
          @wheel="wheel"
          popper-class="select-model"
          @change="ttsModelChange()"
          placeholder="请选择语音合成模型"
          :teleported="false"
        >
          <el-option-group
            v-for="(value, label) in ttsModelOptions"
            :key="value"
            :label="relatedObject(providerOptions, label, 'provider')?.name"
          >
            <el-option
              v-for="item in value.filter((v: any) => v.status === 'SUCCESS')"
              :key="item.id"
              :label="item.name"
              :value="item.id"
              class="flex-between"
            >
              <div class="flex align-center">
                <span
                  v-html="relatedObject(providerOptions, label, 'provider')?.icon"
                  class="model-icon mr-8"
                ></span>
                <span>{{ item.name }}</span>
                <el-tag v-if="item.permission_type === 'PUBLIC'" type="info" class="info-tag ml-8"
                  >公用
                </el-tag>
              </div>
              <el-icon class="check-icon" v-if="item.id === form_data.tts_model_id">
                <Check />
              </el-icon>
            </el-option>
            <!-- 不可用 -->
            <el-option
              v-for="item in value.filter((v: any) => v.status !== 'SUCCESS')"
              :key="item.id"
              :label="item.name"
              :value="item.id"
              class="flex-between"
              disabled
            >
              <div class="flex">
                <span
                  v-html="relatedObject(providerOptions, label, 'provider')?.icon"
                  class="model-icon mr-8"
                ></span>
                <span>{{ item.name }}</span>
                <span class="danger">{{
                  $t('views.application.applicationForm.form.aiModel.unavailable')
                }}</span>
              </div>
              <el-icon class="check-icon" v-if="item.id === form_data.tts_model_id">
                <Check />
              </el-icon>
            </el-option>
          </el-option-group>
        </el-select>
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
import { relatedObject } from '@/utils/utils'
import useStore from '@/stores'
import applicationApi from '@/api/application'
import type { Provider } from '@/api/type/model'
import { MsgError, MsgSuccess, MsgWarning } from '@/utils/message'
import { t } from '@/locales'
import TTSModeParamSettingDialog from '@/views/application/component/TTSModeParamSettingDialog.vue'
import ApiInputFieldTable from './component/ApiInputFieldTable.vue'
import UserInputFieldTable from './component/UserInputFieldTable.vue'
import FileUploadSettingDialog from '@/workflow/nodes/base-node/component/FileUploadSettingDialog.vue'

const { model } = useStore()

const {
  params: { id }
} = app.config.globalProperties.$route as any

const props = defineProps<{ nodeModel: any }>()

const sttModelOptions = ref<any>(null)
const ttsModelOptions = ref<any>(null)
const providerOptions = ref<Array<Provider>>([])
const TTSModeParamSettingDialogRef = ref<InstanceType<typeof TTSModeParamSettingDialog>>()
const UserInputFieldTableFef = ref()
const ApiInputFieldTableFef = ref()
const FileUploadSettingDialogRef = ref<InstanceType<typeof FileUploadSettingDialog>>()

const form = {
  name: '',
  desc: '',
  prologue: t('views.application.prompt.defaultPrologue')
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
    return Promise.reject({ node: props.nodeModel, errMessage: '请选择语音播放模型' })
  }
  if (form_data.value.stt_model_enable && !form_data.value.stt_model_id) {
    return Promise.reject({ node: props.nodeModel, errMessage: '请选择语音输入模型' })
  }
  return baseNodeFormRef.value?.validate().catch((err) => {
    return Promise.reject({ node: props.nodeModel, errMessage: err })
  })
}

function getProvider() {
  model.asyncGetProvider().then((res: any) => {
    providerOptions.value = res?.data
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
    MsgSuccess(t('请选择语音播放模型'))
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
    video: false
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
  getProvider()
  getTTSModel()
  getSTTModel()
})
</script>
<style lang="scss" scoped>
:deep(.el-form-item__label) {
  display: block;
}
</style>
