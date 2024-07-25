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

              <el-form-item
                :label="$t('views.application.applicationForm.form.aiModel.label')"
                prop="model_id"
              >
                <template #label>
                  <div class="flex-between">
                    <span>{{ $t('views.application.applicationForm.form.aiModel.label') }}</span>
                  </div>
                </template>
                <el-select
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
                      <el-icon class="check-icon" v-if="item.id === applicationForm.model_id"
                        ><Check
                      /></el-icon>
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
                      <el-icon class="check-icon" v-if="item.id === applicationForm.model_id"
                        ><Check
                      /></el-icon>
                    </el-option>
                  </el-option-group>
                  <template #footer>
                    <div class="w-full text-left cursor" @click="openCreateModel()">
                      <el-button type="primary" link>
                        <el-icon class="mr-4"><Plus /></el-icon>
                        {{ $t('views.application.applicationForm.form.addModel') }}
                      </el-button>
                    </div>
                  </template>
                </el-select>
              </el-form-item>
              <el-form-item
                :label="$t('views.application.applicationForm.form.prompt.label')"
                prop="model_setting.prompt"
              >
                <template #label>
                  <div class="flex align-center">
                    <div class="flex-between mr-4">
                      <span
                        >{{ $t('views.application.applicationForm.form.prompt.label') }}
                        <span class="danger">*</span></span
                      >
                    </div>
                    <el-tooltip effect="dark" placement="right">
                      <template #content>{{
                        $t('views.application.applicationForm.form.prompt.tooltip', {
                          data: '{data}',
                          question: '{question}'
                        })
                      }}</template>
                      <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
                    </el-tooltip>
                  </div>
                </template>
                <el-input
                  v-model="applicationForm.model_setting.prompt"
                  :rows="6"
                  type="textarea"
                  maxlength="2048"
                  :placeholder="defaultPrompt"
                />
              </el-form-item>
              <el-form-item
                :label="$t('views.application.applicationForm.form.multipleRoundsDialogue')"
                @click.prevent
              >
                <el-switch
                  size="small"
                  v-model="applicationForm.multiple_rounds_dialogue"
                ></el-switch>
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
                        <AppIcon iconName="app-operation" class="mr-4"></AppIcon
                        >{{ $t('views.application.applicationForm.form.paramSetting') }}
                      </el-button>
                      <el-button type="primary" link @click="openDatasetDialog">
                        <el-icon class="mr-4"><Plus /></el-icon
                        >{{ $t('views.application.applicationForm.form.add') }}
                      </el-button>
                    </div>
                  </div>
                </template>
                <div class="w-full">
                  <el-text type="info" v-if="applicationForm.dataset_id_list?.length === 0">{{
                    $t('views.application.applicationForm.form.relatedKnowledgeBaseWhere')
                  }}</el-text>
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
                          <div class="flex align-center">
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
                            <div class="ellipsis">
                              {{ relatedObject(datasetList, item, 'id')?.name }}
                            </div>
                          </div>
                          <el-button text @click="removeDataset(item)">
                            <el-icon><Close /></el-icon>
                          </el-button>
                        </div>
                      </el-card>
                    </el-col>
                  </el-row>
                </div>
              </el-form-item>
              <el-form-item :label="$t('views.application.applicationForm.form.prologue')">
                <MdEditor
                  class="prologue-md-editor"
                  v-model="applicationForm.prologue"
                  :preview="false"
                  :toolbars="[]"
                  :footers="[]"
                />
              </el-form-item>
              <el-form-item @click.prevent>
                <template #label>
                  <div class="flex align-center">
                    <span class="mr-4">{{
                      $t('views.application.applicationForm.form.problemOptimization.label')
                    }}</span>
                    <el-tooltip
                      effect="dark"
                      :content="
                        $t('views.application.applicationForm.form.problemOptimization.tooltip')
                      "
                      placement="right"
                    >
                      <AppIcon iconName="app-warning" class="app-warning-icon"></AppIcon>
                    </el-tooltip>
                  </div>
                </template>
                <el-switch size="small" v-model="applicationForm.problem_optimization"></el-switch>
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
            <div class="mr-12">
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
  </LayoutContainer>
</template>
<script setup lang="ts">
import { reactive, ref, watch, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { groupBy } from 'lodash'
import ParamSettingDialog from './component/ParamSettingDialog.vue'
import AddDatasetDialog from './component/AddDatasetDialog.vue'
import CreateModelDialog from '@/views/template/component/CreateModelDialog.vue'
import SelectProviderDialog from '@/views/template/component/SelectProviderDialog.vue'
import applicationApi from '@/api/application'
import { isAppIcon } from '@/utils/application'
import type { FormInstance, FormRules } from 'element-plus'
import type { ApplicationFormType } from '@/api/type/application'
import type { Provider } from '@/api/type/model'
import { relatedObject } from '@/utils/utils'
import { MsgSuccess } from '@/utils/message'
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

const ParamSettingDialogRef = ref<InstanceType<typeof ParamSettingDialog>>()
const createModelRef = ref<InstanceType<typeof CreateModelDialog>>()
const selectProviderRef = ref<InstanceType<typeof SelectProviderDialog>>()

const applicationFormRef = ref<FormInstance>()
const AddDatasetDialogRef = ref()

const loading = ref(false)
const datasetLoading = ref(false)
const applicationForm = ref<ApplicationFormType>({
  name: '',
  desc: '',
  model_id: '',
  multiple_rounds_dialogue: false,
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
    prompt: defaultPrompt
  },
  problem_optimization: false,
  type: 'SIMPLE'
})

const rules = reactive<FormRules<ApplicationFormType>>({
  name: [
    {
      required: true,
      message: t('views.application.applicationForm.form.appName.placeholder'),
      trigger: 'blur'
    }
  ],
  model_id: [
    {
      required: false,
      message: t('views.application.applicationForm.form.aiModel.placeholder'),
      trigger: 'change'
    }
  ],
  'model_setting.prompt': [
    {
      required: true,
      message: t('views.application.applicationForm.form.prompt.placeholder'),
      trigger: 'blur'
    }
  ]
})
const modelOptions = ref<any>(null)
const providerOptions = ref<Array<Provider>>([])
const datasetList = ref([])

const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      application.asyncPutApplication(id, applicationForm.value, loading).then((res) => {
        MsgSuccess(t('views.application.applicationForm.buttons.saveSuccess'))
      })
    }
  })
}

const openParamSettingDialog = () => {
  ParamSettingDialogRef.value?.open(applicationForm.value.dataset_setting)
}

function refreshParam(data: any) {
  applicationForm.value.dataset_setting = data
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

function refresh() {
  getDataset()
}

onMounted(() => {
  getProvider()
  getModel()
  getDataset()
  getDetail()
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
