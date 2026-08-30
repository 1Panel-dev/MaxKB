<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import type { BaseModelOption, Dict, DynamicFormField, ModelPayload, ModelProviderItem, ModelTypeOption } from '@/api/types'
import SystemSharedModelApi from '@/api/admin/system/shared-resources/model'
import ModelApi from '@/api/admin/workspace/model/model'
import ProviderApi from '@/api/admin/model-provider'
import { MkDynamicsForm, type DynamicFormValue, type FormField } from '@/components/mk-dynamics-form'
import { useStore } from '@/stores'
import { MsgSuccess } from '@/utils/message'
import { isSystemSharedResource } from '@/utils/resource-context'
import ModelAdvancedSettings from '@/views/model/advanced-settings-table/AdvancedSettingsTable.vue'

defineOptions({ name: 'CreateModelDrawer' })

const { auth } = useStore()

const props = withDefaults(defineProps<{ providers?: ModelProviderItem[] }>(), { providers: () => [] })
const emit = defineEmits<{ back: []; refresh: [] }>()

const visible = ref(false)
const loading = ref(false)
const providersLoading = ref(false)
const currentProvider = ref<ModelProviderItem>()
const loadedProviders = ref<ModelProviderItem[]>([])
const providerOptions = computed(() => (props.providers.length ? props.providers : loadedProviders.value))

const modelForm = reactive<ModelPayload>({ credential: {}, model_name: '', model_type: '', name: '', provider: '' })

const modelFormData = computed<Dict<DynamicFormValue>>({
  get: () => ({ ...modelForm.credential, model_name: modelForm.model_name, model_type: modelForm.model_type, name: modelForm.name }),
  set: (value) => {
    const credential = { ...value }
    delete credential.model_name
    delete credential.model_type
    delete credential.name
    modelForm.credential = credential
  },
})

/* 动态表单 */
// 模型类型选择
const modelTypeOptions = ref<ModelTypeOption[]>([])
function loadModelTypes(provider: ModelProviderItem) {
  currentProvider.value = provider
  modelForm.provider = provider.provider
  resetModelSelection()
  loading.value = true
  return ProviderApi.getModelTypeList(provider.provider)
    .then((options) => {
      modelTypeOptions.value = options
    })
    .finally(() => {
      loading.value = false
    })
}

function handleProviderSelect(provider: ModelProviderItem) {
  loadModelTypes(provider)
}

function loadModelProviders() {
  providersLoading.value = true
  return ProviderApi.getProviderList()
    .then((providers) => {
      loadedProviders.value = [...providers].sort((left, right) => left.name.localeCompare(right.name))
    })
    .finally(() => {
      providersLoading.value = false
    })
}

// 基础模型选择 联动动态表单
const dynamicsFormRef = ref<InstanceType<typeof MkDynamicsForm>>()
const dynamicsLoading = ref(false)
const baseModelOptions = ref<BaseModelOption[]>([])
const credentialFields = ref<FormField[]>([])
const modelParamsForm = ref<DynamicFormField[]>([])
function handleModelTypeChange() {
  modelForm.model_name = ''
  modelForm.credential = {}
  baseModelOptions.value = []
  credentialFields.value = []
  modelParamsForm.value = []
  void dynamicsFormRef.value?.render([], modelFormData.value)
  if (!modelForm.model_type) return

  dynamicsLoading.value = true
  ProviderApi.getBaseModelList(modelForm.provider, modelForm.model_type)
    .then((options) => {
      baseModelOptions.value = options
    })
    .finally(() => {
      dynamicsLoading.value = false
    })
}

function handleBaseModelChange() {
  modelForm.credential = {}
  credentialFields.value = []
  modelParamsForm.value = []
  void dynamicsFormRef.value?.render([], modelFormData.value)
  if (!modelForm.model_name) return

  dynamicsLoading.value = true
  Promise.all([
    ProviderApi.getModelCreateForm(modelForm.provider, modelForm.model_type, modelForm.model_name),
    ProviderApi.getBaseModelParamsForm(modelForm.provider, modelForm.model_type, modelForm.model_name),
  ])
    .then(([fields, paramsForm]) => {
      credentialFields.value = fields
      modelParamsForm.value = paramsForm
      return dynamicsFormRef.value?.render(fields, modelFormData.value)
    })
    .finally(() => {
      dynamicsLoading.value = false
    })
}

function handleBack() {
  visible.value = false
  emit('back')
}

// 提交
function handleSubmit() {
  dynamicsFormRef.value?.validate().then(() => {
    loading.value = true
    const payload = { ...modelForm, model_params_form: modelParamsForm.value }
    const request = isSystemSharedResource() ? SystemSharedModelApi.postModel(payload) : ModelApi.postModel(payload)

    return request
      .then(() => {
        return auth.loadAuthBaseProfile().then(() => {
          MsgSuccess('创建成功')
          visible.value = false
          emit('refresh')
        })
      })
      .finally(() => {
        loading.value = false
      })
  })
}

function open(provider: ModelProviderItem) {
  if (!props.providers.length) loadModelProviders()
  loadModelTypes(provider)
  visible.value = true
}

function resetModelSelection() {
  modelForm.model_type = ''
  modelForm.model_name = ''
  modelForm.credential = {}
  modelTypeOptions.value = []
  baseModelOptions.value = []
  credentialFields.value = []
  modelParamsForm.value = []
  void dynamicsFormRef.value?.render([], modelFormData.value)
}

function resetData() {
  currentProvider.value = undefined
  loadedProviders.value = []
  modelForm.name = ''
  modelForm.provider = ''
  resetModelSelection()
  loading.value = false
  providersLoading.value = false
  dynamicsLoading.value = false
}

defineExpose({ open })
</script>

<template>
  <MkDrawer v-model="visible" content-class="h-full p-0!" direction="btt" title="添加模型" @closed="resetData">
    <template #header>
      <div class="flex w-full">
        <h4>添加模型</h4>
        <el-steps :active="1" finish-status="success" class="absolute-center w-75!">
          <el-step title="选择供应商" />
          <el-step title="添加模型" />
        </el-steps>
      </div>
    </template>

    <MkViewLayout :loading="loading || providersLoading" :title="currentProvider?.name ?? ''">
      <template #aside="{ Header }">
        <component :is="Header">
          <el-select model-value="all" class="w-full">
            <el-option label="全部模型" value="all" />
          </el-select>
        </component>

        <el-scrollbar class="min-h-0 flex-1 px-4 pb-4">
          <MkListItem
            v-for="provider in providerOptions"
            :key="provider.provider"
            class="mb-1"
            :active="currentProvider?.provider === provider.provider"
            @click="handleProviderSelect(provider)"
          >
            <span class="h-6 w-6 shrink-0" :innerHTML="provider.icon" />
            <span class="ml-3 min-w-0 flex-1 truncate" :title="provider.name">
              {{ provider.name }}
            </span>
          </MkListItem>
        </el-scrollbar>
      </template>

      <template #default="{ Footer, Header }">
        <component :is="Header">
          <h4>{{ currentProvider?.name }}</h4>
        </component>
        <div class="mx-auto w-full max-w-200 pt-4" v-loading="dynamicsLoading">
          <MkDynamicsForm ref="dynamicsFormRef" v-model="modelFormData" :render-data="credentialFields">
            <template #default>
              <el-form-item class="mk-hide-asterisk" prop="name" :rules="{ required: true, message: '请输入模型名称', trigger: 'blur' }">
                <template #label>
                  <span class="inline-flex items-center gap-2">
                    <span class="mk-required"> 模型名称</span>

                    <el-tooltip content="MaxKB 中自定义的模型名称" placement="right">
                      <MkIcon name="icon_info_outlined" class="text-N600!"></MkIcon>
                    </el-tooltip>
                  </span>
                </template>
                <el-input v-model="modelForm.name" maxlength="64" placeholder="请给基础模型设置一个名称" @blur="modelForm.name = modelForm.name.trim()" />
              </el-form-item>

              <el-form-item class="mk-hide-asterisk" prop="model_type" :rules="{ required: true, message: '请选择模型类型', trigger: 'change' }">
                <template #label>
                  <span class="inline-flex items-center gap-2">
                    <span class="mk-required"> 模型类型</span>
                    <el-tooltip placement="right">
                      <template #content>
                        <p>大语言模型：在智能体中与AI对话的推理模型。</p>
                        <p>向量模型：在知识库中对文档内容进行向量化的模型。</p>
                        <p>语音识别：在智能体中开启语音识别后用于语音转文字的模型。</p>
                        <p>语音合成：在智能体中开启语音播放后用于文字转语音的模型。</p>
                        <p>重排模型：在高级智能体中使用多路召回时，对候选分段进行重新排序的模型。</p>
                        <p>视觉模型：在高级智能体中用于图片理解的视觉模型。</p>
                        <p>图片生成：在高级智能体中用于图片生成的视觉模型。</p>
                        <p>文生视频：在高级智能体中用于文生视频的模型。</p>
                        <p>图生视频：在高级智能体中用于图生视频的模型。</p>
                      </template>
                      <MkIcon name="icon_info_outlined" class="text-N600!"></MkIcon>
                    </el-tooltip>
                  </span>
                </template>
                <el-select v-model="modelForm.model_type" class="w-full" placeholder="请选择模型类型" @change="handleModelTypeChange">
                  <el-option v-for="option in modelTypeOptions" :key="option.value" :label="option.key" :value="option.value" />
                </el-select>
              </el-form-item>

              <el-form-item class="mk-hide-asterisk" prop="model_name" :rules="{ required: true, message: '请选择基础模型，自定义输入基础模型后回车即可', trigger: 'change' }">
                <template #label>
                  <span class="inline-flex items-center gap-2">
                    <span class="mk-required"> 基础模型</span>
                    <span class="text-warning"> 列表中未列出的模型，直接输入模型名称，回车即可添加 </span>
                  </span>
                </template>
                <el-select
                  v-model="modelForm.model_name"
                  allow-create
                  class="w-full"
                  default-first-option
                  filterable
                  placeholder="请选择基础模型，自定义输入基础模型后回车即可"
                  @change="handleBaseModelChange"
                >
                  <el-option v-for="option in baseModelOptions" :key="option.name" :label="option.name" :value="option.name">
                    <template #default>
                      <div class="flex items-center gap-2">
                        <span>{{ option.name }} </span>
                        <el-tooltip v-if="option.desc" :content="option.desc" placement="right">
                          <MkIcon name="icon_info_outlined" class="text-N600!"></MkIcon>
                        </el-tooltip>
                      </div>
                    </template>
                  </el-option>
                </el-select>
              </el-form-item>
            </template>
          </MkDynamicsForm>

          <!-- 高级设置 -->
          <MkCollapse class="mt-2" v-if="modelForm.model_name && modelForm.model_type && modelForm.model_type !== 'RERANKER'" indicator-position="after" trigger-class="mb-2 w-fit">
            <template #label>
              <h6>高级设置</h6>
            </template>
            <ModelAdvancedSettings v-model="modelParamsForm" />
          </MkCollapse>
        </div>
        <component :is="Footer">
          <el-button plain :disabled="loading" @click="visible = false">取消</el-button>
          <el-button plain :disabled="loading" @click="handleBack">上一步</el-button>
          <el-button type="primary" :loading="loading" @click="handleSubmit">保存</el-button>
        </component>
      </template>
    </MkViewLayout>
  </MkDrawer>
</template>
