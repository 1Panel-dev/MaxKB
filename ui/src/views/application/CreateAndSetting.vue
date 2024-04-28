<template>
  <LayoutContainer
    :header="id ? '设置' : '创建应用'"
    :back-to="id ? '' : '-1'"
    class="create-application"
  >
    <el-row v-loading="loading">
      <el-col :span="10">
        <div class="p-24 mb-16" style="padding-bottom: 0">
          <h4 class="title-decoration-1">应用信息</h4>
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
                    <span>应用名称 <span class="danger">*</span></span>
                  </div>
                </template>
                <el-input
                  v-model="applicationForm.name"
                  maxlength="64"
                  placeholder="请输入应用名称"
                  show-word-limit
                />
              </el-form-item>
              <el-form-item label="应用描述">
                <el-input
                  v-model="applicationForm.desc"
                  type="textarea"
                  placeholder="描述该应用的应用场景及用途，如：MaxKB 小助手回答用户提出的 MaxKB 产品使用问题"
                  :rows="3"
                  maxlength="256"
                  show-word-limit
                />
              </el-form-item>

              <el-form-item label="AI 模型" prop="model_id">
                <template #label>
                  <div class="flex-between">
                    <span>AI 模型 </span>
                  </div>
                </template>
                <el-select
                  v-model="applicationForm.model_id"
                  placeholder="请选择 AI 模型"
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
                      <div class="flex">
                        <span
                          v-html="relatedObject(providerOptions, label, 'provider')?.icon"
                          class="model-icon mr-8"
                        ></span>
                        <span>{{ item.name }}</span>
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
                        <span class="danger">（不可用）</span>
                      </div>
                      <el-icon class="check-icon" v-if="item.id === applicationForm.model_id"
                        ><Check
                      /></el-icon>
                    </el-option>
                  </el-option-group>
                  <template #footer>
                    <div class="w-full text-left cursor" @click="openCreateModel()">
                      <el-button type="primary" link>
                        <el-icon class="mr-4"><Plus /></el-icon> 添加模型
                      </el-button>
                    </div>
                  </template>
                </el-select>
              </el-form-item>
              <el-form-item label="提示词" prop="model_setting.prompt">
                <template #label>
                  <div class="flex align-center">
                    <div class="flex-between mr-4">
                      <span>提示词 <span class="danger">*</span></span>
                    </div>
                    <el-tooltip effect="dark" placement="right">
                      <template #content
                        >通过调整提示词内容，可以引导大模型聊天方向，该提示词会被固定在上下文的开头。<br />可以使用变量：{data}
                        是携带知识库中已知信息；{question}是用户提出的问题。</template
                      >
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
              <el-form-item label="多轮对话" @click.prevent>
                <el-switch
                  size="small"
                  v-model="applicationForm.multiple_rounds_dialogue"
                ></el-switch>
              </el-form-item>
              <el-form-item label="关联知识库">
                <template #label>
                  <div class="flex-between">
                    <span>关联知识库</span>
                    <div>
                      <el-button type="primary" link @click="openParamSettingDialog">
                        <AppIcon iconName="app-operation" class="mr-4"></AppIcon>参数设置
                      </el-button>
                      <el-button type="primary" link @click="openDatasetDialog">
                        <el-icon class="mr-4"><Plus /></el-icon>添加
                      </el-button>
                    </div>
                  </div>
                </template>
                <div class="w-full">
                  <el-text type="info" v-if="applicationForm.dataset_id_list?.length === 0"
                    >关联的知识库展示在这里</el-text
                  >
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
                      <el-card class="relate-dataset-card" shadow="never">
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

                            <AppAvatar v-else class="mr-12" shape="square" :size="32">
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
              <el-form-item label="开场白">
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
                    <span class="mr-4">问题优化</span>
                    <el-tooltip
                      effect="dark"
                      content="根据历史聊天优化完善当前问题，更利于匹配知识点。"
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
        <div class="text-right border-t p-16">
          <el-button v-if="!id" @click="router.push({ path: `/application` })"> 取消 </el-button>
          <el-button type="primary" @click="submit(applicationFormRef)" :disabled="loading">
            {{ id ? '保存' : '创建' }}
          </el-button>
        </div>
      </el-col>
      <el-col :span="14" class="p-24 border-l">
        <h4 class="title-decoration-1 mb-16">调试预览</h4>
        <div class="dialog-bg">
          <h4 class="p-24">{{ applicationForm?.name || '应用名称' }}</h4>
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
import ParamSettingDialog from './components/ParamSettingDialog.vue'
import AddDatasetDialog from './components/AddDatasetDialog.vue'
import CreateModelDialog from '@/views/template/component/CreateModelDialog.vue'
import SelectProviderDialog from '@/views/template/component/SelectProviderDialog.vue'
import { MdEditor } from 'md-editor-v3'
import applicationApi from '@/api/application'
import type { FormInstance, FormRules } from 'element-plus'
import type { ApplicationFormType } from '@/api/type/application'
import type { Provider } from '@/api/type/model'
import { relatedObject } from '@/utils/utils'
import { MsgSuccess } from '@/utils/message'
import useStore from '@/stores'

const { model, dataset, application, user } = useStore()

const router = useRouter()
const route = useRoute()
const {
  params: { id }
} = route as any

const defaultPrompt = `已知信息：
{data}
回答要求：
- 请使用简洁且专业的语言来回答用户的问题。
- 如果你不知道答案，请回答“没有在知识库中查找到相关信息，建议咨询相关技术支持或参考官方文档进行操作”。
- 避免提及你是从已知信息中获得的知识。
- 请保证答案与已知信息中描述的一致。
- 请使用 Markdown 语法优化答案的格式。
- 已知信息中的图片、链接地址和脚本语言请直接返回。
- 请使用与问题相同的语言来回答。
问题：
{question}
`

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
  prologue: `您好，我是 MaxKB 小助手，您可以向我提出 MaxKB 使用问题。
- MaxKB 主要功能有什么？
- MaxKB 支持哪些大语言模型？
- MaxKB 支持哪些文档类型？`,
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
  problem_optimization: false
})

const rules = reactive<FormRules<ApplicationFormType>>({
  name: [{ required: true, message: '请输入应用名称', trigger: 'blur' }],
  model_id: [
    {
      required: false,
      message: '请选择模型',
      trigger: 'change'
    }
  ],
  'model_setting.prompt': [{ required: true, message: '请输入提示词', trigger: 'blur' }]
})
const modelOptions = ref<any>(null)
const providerOptions = ref<Array<Provider>>([])
const datasetList = ref([])

const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      if (id) {
        application.asyncPutApplication(id, applicationForm.value, loading).then((res) => {
          MsgSuccess('保存成功')
        })
      } else {
        applicationApi.postApplication(applicationForm.value, loading).then((res) => {
          MsgSuccess('创建成功')
          router.push({ path: `/application` })
        })
      }
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
  if (id) {
    application.asyncGetApplicationDataset(id, datasetLoading).then((res: any) => {
      datasetList.value = res.data
    })
  } else {
    dataset.asyncGetAllDataset(datasetLoading).then((res: any) => {
      datasetList.value = res.data?.filter((v: any) => v.user_id === user.userInfo?.id)
    })
  }
}

function getModel() {
  loading.value = true
  if (id) {
    applicationApi
      .getApplicationModel(id)
      .then((res: any) => {
        modelOptions.value = groupBy(res?.data, 'provider')
        loading.value = false
      })
      .catch(() => {
        loading.value = false
      })
  } else {
    model
      .asyncGetModel()
      .then((res: any) => {
        modelOptions.value = groupBy(res?.data, 'provider')
        loading.value = false
      })
      .catch(() => {
        loading.value = false
      })
  }
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
  if (id) {
    getDetail()
  }
})
</script>
<style lang="scss" scoped>
.create-application {
  .relate-dataset-card {
    color: var(--app-text-color);
    border-radius: 4px;
  }
  .dialog-bg {
    border-radius: 8px;
    background: var(--dialog-bg-gradient-color);
    overflow: hidden;
    box-sizing: border-box;
  }
  .scrollbar-height-left {
    height: calc(var(--app-main-height) - 127px);
  }
  .scrollbar-height {
    height: calc(var(--app-main-height) - 150px);
  }
}
.model-icon {
  width: 20px;
}
.check-icon {
  position: absolute;
  right: 10px;
}
.prologue-md-editor {
  height: 150px;
}
</style>
