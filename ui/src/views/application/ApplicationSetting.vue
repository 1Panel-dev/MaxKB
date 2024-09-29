<template>
  <LayoutContainer class="create-application">
    <template #header>
      <div class="flex-between w-full">
        <h3>
          {{ $t('views.application.applicationForm.title.edit') }}
        </h3>
        <el-button type="primary" @click="submit(applicationFormRef)" :disabled="loading">
          保存并发布
        </el-button>
      </div>
    </template>
    <el-row v-loading="loading">
      <el-col :span="10">
        <div class="p-24 mb-16" style="padding-bottom: 0">
          <h4 class="title-decoration-1">
            {{ $t('views.application.applicationForm.title.info') }}
          </h4>
        </div>
        <div class="scrollbar-height-left">
          <el-scrollbar>
            <el-form
              hide-required-asterisk
              ref="applicationFormRef"
              :model="applicationForm"
              :rules="rules"
              label-position="top"
              require-asterisk-position="right"
              class="p-24"
              style="padding-top: 0"
            >
              <el-form-item prop="name">
                <template #label>
                  <div class="flex-between">
                    <span
                      >{{ $t('views.application.applicationForm.form.appName.label') }}
                      <span class="danger">*</span></span
                    >
                  </div>
                </template>
                <el-input
                  v-model="applicationForm.name"
                  maxlength="64"
                  :placeholder="$t('views.application.applicationForm.form.appName.placeholder')"
                  show-word-limit
                  @blur="applicationForm.name = applicationForm.name?.trim()"
                />
              </el-form-item>
              <el-form-item
                :label="$t('views.application.applicationForm.form.appDescription.label')"
              >
                <el-input
                  v-model="applicationForm.desc"
                  type="textarea"
                  :placeholder="
                    $t('views.application.applicationForm.form.appDescription.placeholder')
                  "
                  :rows="3"
                  maxlength="256"
                  show-word-limit
                />
              </el-form-item>

              <el-form-item :label="$t('views.application.applicationForm.form.aiModel.label')">
                <template #label>
                  <div class="flex-between">
                    <span>{{ $t('views.application.applicationForm.form.aiModel.label') }}</span>
                    <el-button
                      type="primary"
                      link
                      @click="openAIParamSettingDialog"
                      :disabled="!applicationForm.model_id"
                    >
                      {{ $t('views.application.applicationForm.form.paramSetting') }}
                    </el-button>
                  </div>
                </template>
                <el-select
                  @change="model_change"
                  v-model="applicationForm.model_id"
                  :placeholder="$t('views.application.applicationForm.form.aiModel.placeholder')"
                  class="w-full"
                  popper-class="select-model"
                  :clearable="true"
                >
                  <el-option-group
                    v-for="(value, label) in modelOptions"
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
                        <el-tag
                          v-if="item.permission_type === 'PUBLIC'"
                          type="info"
                          class="info-tag ml-8"
                          >公用
                        </el-tag>
                      </div>
                      <el-icon class="check-icon" v-if="item.id === applicationForm.model_id">
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
                      <el-icon class="check-icon" v-if="item.id === applicationForm.model_id">
                        <Check />
                      </el-icon>
                    </el-option>
                  </el-option-group>
                  <template #footer>
                    <div class="w-full text-left cursor" @click="openCreateModel()">
                      <el-button type="primary" link>
                        <el-icon class="mr-4">
                          <Plus />
                        </el-icon>
                        {{ $t('views.application.applicationForm.form.addModel') }}
                      </el-button>
                    </div>
                  </template>
                </el-select>
              </el-form-item>
              <el-form-item label="角色设定">
                <MdEditorMagnify
                  title="角色设定"
                  v-model="applicationForm.model_setting.system"
                  style="height: 120px"
                  @submitDialog="submitSystemDialog"
                  placeholder="你是 xxx 小助手"
                />
              </el-form-item>
              <el-form-item
                :label="$t('views.application.applicationForm.form.prompt.label')"
                prop="model_setting.no_references_prompt"
                :rules="{
                  required: applicationForm.model_id,
                  message: '请输入提示词',
                  trigger: 'blur'
                }"
              >
                <template #label>
                  <div class="flex align-center">
                    <span class="mr-4"
                      >{{ $t('views.application.applicationForm.form.prompt.label') }}
                      (无引用知识库)
                    </span>
                    <el-tooltip
                      effect="dark"
                      content="通过调整提示词内容，可以引导大模型聊天方向，该提示词会被固定在上下文的开头。可以使用变量：{question} 是用户提出问题的占位符。"
                      placement="right"
                    >
                      <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
                    </el-tooltip>
                    <span class="danger ml-4" v-if="applicationForm.model_id">*</span>
                  </div>
                </template>

                <MdEditorMagnify
                  title="提示词(无引用知识库)"
                  v-model="applicationForm.model_setting.no_references_prompt"
                  style="height: 120px"
                  @submitDialog="submitNoReferencesPromptDialog"
                  placeholder="{question}"
                />
              </el-form-item>
              <el-form-item label="历史聊天记录" @click.prevent>
                <el-input-number
                  v-model="applicationForm.dialogue_number"
                  :min="0"
                  :value-on-clear="0"
                  controls-position="right"
                  class="w-full"
                />
              </el-form-item>
              <el-form-item
                label="$t('views.application.applicationForm.form.relatedKnowledgeBase')"
              >
                <template #label>
                  <div class="flex-between">
                    <span>{{
                      $t('views.application.applicationForm.form.relatedKnowledgeBase')
                    }}</span>
                    <div>
                      <el-button type="primary" link @click="openParamSettingDialog">
                        <AppIcon iconName="app-operation" class="mr-4"></AppIcon>
                        {{ $t('views.application.applicationForm.form.paramSetting') }}
                      </el-button>
                      <el-button type="primary" link @click="openDatasetDialog">
                        <el-icon class="mr-4">
                          <Plus />
                        </el-icon>
                        {{ $t('views.application.applicationForm.form.add') }}
                      </el-button>
                    </div>
                  </div>
                </template>
                <div class="w-full">
                  <el-text type="info" v-if="applicationForm.dataset_id_list?.length === 0"
                    >{{ $t('views.application.applicationForm.form.relatedKnowledgeBaseWhere') }}
                  </el-text>
                  <el-row :gutter="12" v-else>
                    <el-col
                      :xs="24"
                      :sm="24"
                      :md="24"
                      :lg="12"
                      :xl="12"
                      class="mb-8"
                      v-for="(item, index) in applicationForm.dataset_id_list"
                      :key="index"
                    >
                      <el-card class="relate-dataset-card border-r-4" shadow="never">
                        <div class="flex-between">
                          <div class="flex align-center" style="width: 80%">
                            <AppAvatar
                              v-if="relatedObject(datasetList, item, 'id')?.type === '1'"
                              class="mr-8 avatar-purple"
                              shape="square"
                              :size="32"
                            >
                              <img src="@/assets/icon_web.svg" style="width: 58%" alt="" />
                            </AppAvatar>

                            <AppAvatar v-else class="mr-8 avatar-blue" shape="square" :size="32">
                              <img src="@/assets/icon_document.svg" style="width: 58%" alt="" />
                            </AppAvatar>
                            <auto-tooltip
                              :content="relatedObject(datasetList, item, 'id')?.name"
                              style="width: 80%"
                            >
                              {{ relatedObject(datasetList, item, 'id')?.name }}
                            </auto-tooltip>
                          </div>
                          <el-button text @click="removeDataset(item)">
                            <el-icon>
                              <Close />
                            </el-icon>
                          </el-button>
                        </div>
                      </el-card>
                    </el-col>
                  </el-row>
                </div>
              </el-form-item>
              <el-form-item
                :label="$t('views.application.applicationForm.form.prompt.label')"
                prop="model_setting.prompt"
                :rules="{
                  required: applicationForm.model_id,
                  message: '请输入提示词',
                  trigger: 'blur'
                }"
              >
                <template #label>
                  <div class="flex align-center">
                    <span class="mr-4">
                      {{ $t('views.application.applicationForm.form.prompt.label') }}
                      (引用知识库)
                    </span>
                    <el-tooltip
                      effect="dark"
                      content="通过调整提示词内容，可以引导大模型聊天方向，该提示词会被固定在上下文的开头。可以使用变量：{data} 是引用知识库中分段的占位符；{question} 是用户提出问题的占位符。"
                      placement="right"
                    >
                      <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
                    </el-tooltip>
                    <span class="danger ml-4" v-if="applicationForm.model_id">*</span>
                  </div>
                </template>

                <MdEditorMagnify
                  title="提示词(引用知识库)"
                  v-model="applicationForm.model_setting.prompt"
                  style="height: 150px"
                  @submitDialog="submitPromptDialog"
                  :placeholder="defaultPrompt"
                />
              </el-form-item>
              <el-form-item :label="$t('views.application.applicationForm.form.prologue')">
                <MdEditorMagnify
                  title="开场白"
                  v-model="applicationForm.prologue"
                  style="height: 150px"
                  @submitDialog="submitPrologueDialog"
                />
              </el-form-item>

              <el-form-item>
                <template #label>
                  <div class="flex-between">
                    <div class="flex align-center">
                      <span class="mr-4">语音输入</span>
                      <el-tooltip
                        effect="dark"
                        content="开启后，需要设定语音转文本模型，语音输入完成后会转化为文字直接发送提问"
                        placement="right"
                      >
                        <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
                      </el-tooltip>
                    </div>
                    <el-switch size="small" v-model="applicationForm.stt_model_enable" />
                  </div>
                </template>
                <el-select
                  v-if="applicationForm.stt_model_enable"
                  v-model="applicationForm.stt_model_id"
                  class="w-full"
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
                        <el-tag
                          v-if="item.permission_type === 'PUBLIC'"
                          type="info"
                          class="info-tag ml-8"
                          >公用
                        </el-tag>
                      </div>
                      <el-icon class="check-icon" v-if="item.id === applicationForm.stt_model_id">
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
                      <el-icon class="check-icon" v-if="item.id === applicationForm.stt_model_id">
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
                    <el-switch size="small" v-model="applicationForm.tts_model_enable" />
                  </div>
                </template>
                <el-radio-group
                  v-model="applicationForm.tts_type"
                  v-if="applicationForm.tts_model_enable"
                >
                  <el-radio value="BROWSER">浏览器播放(免费)</el-radio>
                  <el-radio value="TTS">TTS模型</el-radio>
                </el-radio-group>
                <el-select
                  v-if="applicationForm.tts_type === 'TTS' && applicationForm.tts_model_enable"
                  v-model="applicationForm.tts_model_id"
                  class="w-full"
                  popper-class="select-model"
                  placeholder="请选择语音合成模型"
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
                        <el-tag
                          v-if="item.permission_type === 'PUBLIC'"
                          type="info"
                          class="info-tag ml-8"
                          >公用
                        </el-tag>
                      </div>
                      <el-icon class="check-icon" v-if="item.id === applicationForm.tts_model_id">
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
                      <el-icon class="check-icon" v-if="item.id === applicationForm.tts_model_id">
                        <Check />
                      </el-icon>
                    </el-option>
                  </el-option-group>
                </el-select>
              </el-form-item>
            </el-form>
          </el-scrollbar>
        </div>
      </el-col>
      <el-col :span="14" class="p-24 border-l">
        <h4 class="title-decoration-1 mb-16">
          {{ $t('views.application.applicationForm.form.apptest') }}
        </h4>
        <div class="dialog-bg">
          <div class="flex align-center p-24">
            <div
              class="edit-avatar mr-12"
              @mouseenter="showEditIcon = true"
              @mouseleave="showEditIcon = false"
            >
              <AppAvatar
                v-if="isAppIcon(applicationForm?.icon)"
                shape="square"
                :size="32"
                style="background: none"
              >
                <img :src="applicationForm?.icon" alt="" />
              </AppAvatar>
              <AppAvatar
                v-else-if="applicationForm?.name"
                :name="applicationForm?.name"
                pinyinColor
                shape="square"
                :size="32"
              />
              <AppAvatar
                v-if="showEditIcon"
                shape="square"
                class="edit-mask"
                :size="32"
                @click="openEditAvatar"
              >
                <el-icon><EditPen /></el-icon>
              </AppAvatar>
            </div>
            <h4>
              {{
                applicationForm?.name || $t('views.application.applicationForm.form.appName.label')
              }}
            </h4>
          </div>
          <div class="scrollbar-height">
            <AiChat :data="applicationForm"></AiChat>
          </div>
        </div>
      </el-col>
    </el-row>

    <AIModeParamSettingDialog ref="AIModeParamSettingDialogRef" @refresh="refreshForm" />
    <ParamSettingDialog ref="ParamSettingDialogRef" @refresh="refreshParam" />
    <AddDatasetDialog
      ref="AddDatasetDialogRef"
      @addData="addDataset"
      :data="datasetList"
      @refresh="refresh"
      :loading="datasetLoading"
    />

    <!-- 添加模版 -->
    <CreateModelDialog
      ref="createModelRef"
      @submit="getModel"
      @change="openCreateModel($event)"
    ></CreateModelDialog>
    <SelectProviderDialog ref="selectProviderRef" @change="openCreateModel($event)" />
    <EditAvatarDialog ref="EditAvatarDialogRef" @refresh="refreshIcon" />
  </LayoutContainer>
</template>
<script setup lang="ts">
import { reactive, ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { groupBy } from 'lodash'
import AIModeParamSettingDialog from './component/AIModeParamSettingDialog.vue'
import ParamSettingDialog from './component/ParamSettingDialog.vue'
import AddDatasetDialog from './component/AddDatasetDialog.vue'
import CreateModelDialog from '@/views/template/component/CreateModelDialog.vue'
import SelectProviderDialog from '@/views/template/component/SelectProviderDialog.vue'

import EditAvatarDialog from '@/views/application-overview/component/EditAvatarDialog.vue'
import applicationApi from '@/api/application'
import { isAppIcon } from '@/utils/application'
import type { FormInstance, FormRules } from 'element-plus'
import type { ApplicationFormType } from '@/api/type/application'
import type { Provider } from '@/api/type/model'
import { relatedObject } from '@/utils/utils'
import { MsgSuccess, MsgWarning } from '@/utils/message'
import useStore from '@/stores'
import { t } from '@/locales'

const { model, application } = useStore()

const route = useRoute()
const {
  params: { id }
} = route as any
// @ts-ignore
const defaultPrompt = t('views.application.prompt.defaultPrompt', {
  data: '{data}',
  question: '{question}'
})

const AIModeParamSettingDialogRef = ref<InstanceType<typeof AIModeParamSettingDialog>>()
const ParamSettingDialogRef = ref<InstanceType<typeof ParamSettingDialog>>()
const createModelRef = ref<InstanceType<typeof CreateModelDialog>>()
const selectProviderRef = ref<InstanceType<typeof SelectProviderDialog>>()

const applicationFormRef = ref<FormInstance>()
const AddDatasetDialogRef = ref()
const EditAvatarDialogRef = ref()

const loading = ref(false)
const datasetLoading = ref(false)
const applicationForm = ref<ApplicationFormType>({
  name: '',
  desc: '',
  model_id: '',
  dialogue_number: 1,
  prologue: t('views.application.prompt.defaultPrologue'),
  dataset_id_list: [],
  dataset_setting: {
    top_n: 3,
    similarity: 0.6,
    max_paragraph_char_number: 5000,
    search_mode: 'embedding',
    no_references_setting: {
      status: 'ai_questioning',
      value: '{question}'
    }
  },
  model_setting: {
    prompt: defaultPrompt,
    system: '你是 xxx 小助手',
    no_references_prompt: '{question}'
  },
  model_params_setting: {},
  problem_optimization: false,
  problem_optimization_prompt:
    '()里面是用户问题,根据上下文回答揣测用户问题({question}) 要求: 输出一个补全问题,并且放在<data></data>标签中',
  stt_model_id: '',
  tts_model_id: '',
  stt_model_enable: false,
  tts_model_enable: false,
  tts_type: 'BROWSER',
  type: 'SIMPLE'
})

const rules = reactive<FormRules<ApplicationFormType>>({
  name: [
    {
      required: true,
      message: t('views.application.applicationForm.form.appName.placeholder'),
      trigger: 'blur'
    }
  ]
})
const modelOptions = ref<any>(null)
const providerOptions = ref<Array<Provider>>([])
const datasetList = ref([])
const sttModelOptions = ref<any>(null)
const ttsModelOptions = ref<any>(null)
const showEditIcon = ref(false)

function submitPrologueDialog(val: string) {
  applicationForm.value.prologue = val
}
function submitPromptDialog(val: string) {
  applicationForm.value.model_setting.prompt = val
}
function submitNoReferencesPromptDialog(val: string) {
  applicationForm.value.model_setting.no_references_prompt = val
}
function submitSystemDialog(val: string) {
  applicationForm.value.model_setting.system = val
}

const submit = async (formEl: FormInstance | undefined) => {
  if (
    applicationForm.value.tts_model_enable &&
    !applicationForm.value.tts_model_id &&
    applicationForm.value.tts_type === 'TTS'
  ) {
    MsgWarning(t('请选择语音播放模型'))
    return
  }
  if (applicationForm.value.stt_model_enable && !applicationForm.value.stt_model_id) {
    MsgWarning(t('请选择语音输入模型'))
    return
  }
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      application.asyncPutApplication(id, applicationForm.value, loading).then((res) => {
        MsgSuccess(t('views.application.applicationForm.buttons.saveSuccess'))
      })
    }
  })
}
const model_change = (model_id?: string) => {
  if (model_id) {
    AIModeParamSettingDialogRef.value?.reset_default(model_id, id)
  } else {
    refreshForm({})
  }
}
const openAIParamSettingDialog = () => {
  const model_id = applicationForm.value.model_id
  if (!model_id) {
    MsgSuccess(t('请选择AI 模型'))
    return
  }
  AIModeParamSettingDialogRef.value?.open(model_id, id, applicationForm.value.model_params_setting)
}

const openParamSettingDialog = () => {
  ParamSettingDialogRef.value?.open(applicationForm.value)
}

function refreshParam(data: any) {
  applicationForm.value = { ...applicationForm.value, ...data }
}

function refreshForm(data: any) {
  applicationForm.value.model_params_setting = data
}

const openCreateModel = (provider?: Provider) => {
  if (provider && provider.provider) {
    createModelRef.value?.open(provider)
  } else {
    selectProviderRef.value?.open()
  }
}

function removeDataset(id: any) {
  if (applicationForm.value.dataset_id_list) {
    applicationForm.value.dataset_id_list.splice(
      applicationForm.value.dataset_id_list.indexOf(id),
      1
    )
  }
}

function addDataset(val: Array<string>) {
  applicationForm.value.dataset_id_list = val
}

function openDatasetDialog() {
  AddDatasetDialogRef.value.open(applicationForm.value.dataset_id_list)
}

function getDetail() {
  application.asyncGetApplicationDetail(id, loading).then((res: any) => {
    applicationForm.value = res.data
    applicationForm.value.model_id = res.data.model
    applicationForm.value.stt_model_id = res.data.stt_model
    applicationForm.value.tts_model_id = res.data.tts_model
    applicationForm.value.tts_type = res.data.tts_type
    applicationForm.value.model_setting.no_references_prompt =
      res.data.model_setting.no_references_prompt || '{question}'
  })
}

function getDataset() {
  application.asyncGetApplicationDataset(id, datasetLoading).then((res: any) => {
    datasetList.value = res.data
  })
}

function getModel() {
  loading.value = true
  applicationApi
    .getApplicationModel(id)
    .then((res: any) => {
      modelOptions.value = groupBy(res?.data, 'provider')
      loading.value = false
    })
    .catch(() => {
      loading.value = false
    })
}

function getSTTModel() {
  loading.value = true
  applicationApi
    .getApplicationSTTModel(id)
    .then((res: any) => {
      sttModelOptions.value = groupBy(res?.data, 'provider')
      loading.value = false
    })
    .catch(() => {
      loading.value = false
    })
}

function getTTSModel() {
  loading.value = true
  applicationApi
    .getApplicationTTSModel(id)
    .then((res: any) => {
      ttsModelOptions.value = groupBy(res?.data, 'provider')
      loading.value = false
    })
    .catch(() => {
      loading.value = false
    })
}

function getProvider() {
  loading.value = true
  model
    .asyncGetProvider()
    .then((res: any) => {
      providerOptions.value = res?.data
      loading.value = false
    })
    .catch(() => {
      loading.value = false
    })
}

function openEditAvatar() {
  EditAvatarDialogRef.value.open(applicationForm.value)
}
function refreshIcon() {
  getDetail()
}

function refresh() {
  getDataset()
}

onMounted(() => {
  getProvider()
  getModel()
  getDataset()
  getDetail()
  getSTTModel()
  getTTSModel()
})
</script>
<style lang="scss" scoped>
.create-application {
  .relate-dataset-card {
    color: var(--app-text-color);
  }

  .dialog-bg {
    border-radius: 8px;
    background: var(--dialog-bg-gradient-color);
    overflow: hidden;
    box-sizing: border-box;
  }

  .scrollbar-height-left {
    height: calc(var(--app-main-height) - 64px);
  }

  .scrollbar-height {
    height: calc(var(--app-main-height) - 160px);
  }
}

.prologue-md-editor {
  height: 150px;
}
</style>
