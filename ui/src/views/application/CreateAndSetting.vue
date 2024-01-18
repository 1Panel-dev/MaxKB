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
                  maxlength="500"
                  show-word-limit
                />
              </el-form-item>
              <el-form-item prop="model_id">
                <template #label>
                  <div class="flex-between">
                    <span>AI 模型 <span class="danger">*</span></span>

                    <el-button type="primary" link @click="promptChange('open')">提示词</el-button>
                  </div>
                </template>
                <el-select
                  v-model="applicationForm.model_id"
                  placeholder="请选择 AI 模型"
                  style="width: 100%"
                >
                  <el-option-group
                    v-for="(value, label) in modelOptions"
                    :key="value"
                    :label="realatedObject(providerOptions, label, 'provider')?.name"
                  >
                    <el-option
                      v-for="item in value"
                      :key="item.id"
                      :label="item.name"
                      :value="item.id"
                      class="flex-between"
                    >
                      <div class="flex">
                        <span
                          v-html="realatedObject(providerOptions, label, 'provider')?.icon"
                          class="model-icon mr-8"
                        ></span>
                        <span>{{ item.name }}</span>
                      </div>
                      <el-icon class="check-icon" v-if="item.id === applicationForm.model_id"
                        ><Check
                      /></el-icon>
                    </el-option>
                  </el-option-group>
                  <template #footer>
                    <el-button type="primary" link @click="openCreateModel">
                      <el-icon class="mr-4"><Plus /></el-icon> 添加模型
                    </el-button>
                  </template>
                </el-select>
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

                    <el-popover :visible="popoverVisible" :width="300" trigger="click">
                      <template #reference>
                        <el-button type="primary" link @click="popoverVisible = !popoverVisible"
                          >参数设置</el-button
                        >
                      </template>
                      <div class="dataset_setting">
                        <div class="form-item mb-16 p-8">
                          <div class="title flex align-center mb-8">
                            <span style="margin-right: 4px">相似度</span>
                            <el-tooltip
                              effect="dark"
                              content="相似度越高相关性越强。"
                              placement="right"
                            >
                              <el-icon style="font-size: 16px">
                                <Warning />
                              </el-icon>
                            </el-tooltip>
                          </div>
                          <div @click.stop>
                            高于
                            <el-input-number
                              v-model="applicationForm.dataset_setting.similarity"
                              :min="0"
                              :max="1"
                              :precision="3"
                              :step="0.1"
                              controls-position="right"
                              style="width: 100px"
                              size="small"
                            />
                          </div>
                        </div>
                        <div class="form-item mb-16 p-8">
                          <div class="title mb-8">引用分段数</div>
                          <div @click.stop>
                            TOP
                            <el-input-number
                              v-model="applicationForm.dataset_setting.top_n"
                              :min="1"
                              :max="10"
                              controls-position="right"
                              style="width: 100px"
                              size="small"
                            />
                            个分段
                          </div>
                        </div>

                        <div class="form-item mb-16 p-8">
                          <div class="title mb-8">最多引用字符数</div>
                          <div class="flex align-center">
                            <el-slider
                              v-model="applicationForm.dataset_setting.max_paragraph_char_number"
                              show-input
                              :show-input-controls="false"
                              :min="500"
                              :max="10000"
                              style="width: 200px"
                              size="small"
                            />
                            <span class="ml-4">个字符</span>
                          </div>
                        </div>
                      </div>
                      <div class="text-right">
                        <el-button type="primary" @click="popoverVisible = false" size="small"
                          >确认</el-button
                        >
                      </div>
                    </el-popover>
                  </div>
                </template>
                <div class="w-full">
                  <el-row :gutter="12">
                    <el-col :xs="24" :sm="24" :md="12" :lg="12" :xl="12" class="mb-8">
                      <CardAdd
                        title="关联知识库"
                        @click="openDatasetDialog"
                        style="min-height: 50px; font-size: 14px"
                      />
                    </el-col>
                    <el-col
                      :xs="24"
                      :sm="24"
                      :md="12"
                      :lg="12"
                      :xl="12"
                      class="mb-8"
                      v-for="(item, index) in applicationForm.dataset_id_list"
                      :key="index"
                    >
                      <el-card class="relate-dataset-card" shadow="never">
                        <div class="flex-between">
                          <div class="flex align-center">
                            <AppAvatar class="mr-12" shape="square" :size="32">
                              <img src="@/assets/icon_document.svg" style="width: 58%" alt="" />
                            </AppAvatar>
                            <div class="ellipsis">
                              {{ realatedObject(datasetList, item, 'id')?.name }}
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
                    <span>问题优化</span>
                    <el-tooltip
                      effect="dark"
                      content="根据历史聊天优化完善当前问题，更利于匹配知识点。"
                      placement="right"
                    >
                      <el-icon style="font-size: 16px">
                        <Warning />
                      </el-icon>
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
    <el-dialog v-model="dialogFormVisible" title="提示词">
      <el-alert type="info" show-icon class="mb-16" :closable="false">
        <p>通过调整提示词内容，可以引导大模型聊天方向，该提示词会被固定在上下文的开头。</p>
        <p>可以使用变量：{data} 是携带知识库中已知信息；{question}是用户提出的问题。</p>
      </el-alert>
      <el-input
        v-model="model_setting_prompt"
        :rows="13"
        type="textarea"
        :placeholder="defaultPrompt"
      />
      <template #footer>
        <span class="dialog-footer">
          <el-button @click="dialogFormVisible = false">取消</el-button>
          <el-button type="primary" @click="promptChange('close')"> 确认 </el-button>
        </span>
      </template>
    </el-dialog>
    <AddDatasetDialog
      ref="AddDatasetDialogRef"
      @addData="addDataset"
      :data="datasetList"
      @refresh="refresh"
      :loading="datasetLoading"
    />
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
import { groupBy, cloneDeep } from 'lodash'
import AddDatasetDialog from './components/AddDatasetDialog.vue'
import CreateModelDialog from '@/views/template/component/CreateModelDialog.vue'
import SelectProviderDialog from '@/views/template/component/SelectProviderDialog.vue'
import { MdEditor } from 'md-editor-v3'
import applicationApi from '@/api/application'
import type { FormInstance, FormRules } from 'element-plus'
import type { ApplicationFormType } from '@/api/type/application'
import type { Provider } from '@/api/type/model'
import { realatedObject } from '@/utils/utils'
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

- 请简洁和专业的来回答用户的问题。

- 如果你不知道答案，请回答“没有在知识库中查找到相关信息，建议咨询相关技术支持或参考官方文档进行操作”。

- 避免提及你是从已知信息中获得的知识。

- 请保证答案与已知信息中描述的一致。

- 请使用 Markdown 语法优化答案的格式。

- 已知信息中的图片、链接地址和脚本语言请直接返回。

- 请使用与问题相同的语言来回答。

问题：

{question}
    `

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
    max_paragraph_char_number: 5000
  },
  model_setting: {
    prompt: defaultPrompt
  },
  problem_optimization: false
})

const popoverVisible = ref(false)

const rules = reactive<FormRules<ApplicationFormType>>({
  name: [{ required: true, message: '请输入应用名称', trigger: 'blur' }],
  model_id: [
    {
      required: true,
      message: '请选择模型',
      trigger: 'change'
    }
  ]
})
const modelOptions = ref<any>(null)
const providerOptions = ref<Array<Provider>>([])
const datasetList = ref([])
const dialogFormVisible = ref(false)

const model_setting_prompt = ref('')

function promptChange(val: string) {
  if (val === 'open') {
    dialogFormVisible.value = true
    model_setting_prompt.value = applicationForm.value.model_setting.prompt
  } else if (val === 'close') {
    dialogFormVisible.value = false
    applicationForm.value.model_setting.prompt = model_setting_prompt.value
  }
}

const submit = async (formEl: FormInstance | undefined) => {
  if (!formEl) return
  await formEl.validate((valid, fields) => {
    if (valid) {
      if (id) {
        applicationApi.putApplication(id, applicationForm.value, loading).then((res) => {
          MsgSuccess('保存成功')
        })
      } else {
        applicationApi.postApplication(applicationForm.value, loading).then((res) => {
          MsgSuccess('创建成功')
          router.push({ path: `/application` })
        })
      }
    } else {
      console.log('error submit!')
    }
  })
}

const openCreateModel = (provider?: Provider) => {
  if (provider && provider.provider) {
    createModelRef.value?.open(provider)
  } else {
    selectProviderRef.value?.open()
  }
}

function removeDataset(id: string) {
  applicationForm.value.dataset_id_list.splice(applicationForm.value.dataset_id_list.indexOf(id), 1)
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
    dataset.asyncGetAllDateset(datasetLoading).then((res: any) => {
      datasetList.value = res.data?.filter((v: any) => v.user_id === user.userInfo?.id)
    })
  }
}

function getModel() {
  loading.value = true
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
.dataset_setting {
  .form-item {
    background: var(--app-layout-bg-color);
  }
}
</style>
