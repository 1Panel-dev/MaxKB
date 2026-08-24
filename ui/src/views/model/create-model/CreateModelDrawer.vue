<script setup lang="ts">
import { computed, nextTick, reactive, ref } from 'vue'
import type { FormInstance, FormRules } from 'element-plus'
import { InfoFilled } from '@element-plus/icons-vue'
import type {
  BaseModelOption,
  DynamicFormField,
  ModelPayload,
  ModelProviderItem,
  ModelTypeOption,
} from '@/api/types'
import ModelApi from '@/api/admin/workspace/model/model'
import ProviderApi from '@/api/admin/workspace/model/provider'
import { MsgSuccess } from '@/utils/message'

defineOptions({ name: 'CreateModelDrawer' })

defineProps<{
  providers: ModelProviderItem[]
}>()
const emit = defineEmits<{
  back: []
  refresh: []
}>()

const formRef = ref<FormInstance>()
const visible = ref(false)
const loading = ref(false)
const optionLoading = ref(false)
const selectedProvider = ref<ModelProviderItem>()
const modelTypeOptions = ref<ModelTypeOption[]>([])
const baseModelOptions = ref<BaseModelOption[]>([])
const credentialFields = ref<DynamicFormField[]>([])
const modelParamsForm = ref<DynamicFormField[]>([])

const modelForm = reactive<ModelPayload>({
  credential: {},
  model_name: '',
  model_type: '',
  name: '',
  provider: '',
})

const formRules = computed<FormRules>(() => {
  const rules: FormRules = {
    model_name: [{ required: true, message: '请选择或输入基础模型', trigger: 'change' }],
    model_type: [{ required: true, message: '请选择模型类型', trigger: 'change' }],
    name: [{ required: true, message: '请输入模型名称', trigger: 'blur' }],
  }

  return rules
})

function resetModelSelection() {
  modelForm.model_type = ''
  modelForm.model_name = ''
  modelForm.credential = {}
  modelTypeOptions.value = []
  baseModelOptions.value = []
  credentialFields.value = []
  modelParamsForm.value = []
  formRef.value?.clearValidate()
}

function resetData() {
  selectedProvider.value = undefined
  modelForm.name = ''
  modelForm.provider = ''
  resetModelSelection()
  loading.value = false
  optionLoading.value = false
}

function loadModelTypes(provider: ModelProviderItem) {
  selectedProvider.value = provider
  modelForm.provider = provider.provider
  resetModelSelection()
  optionLoading.value = true
  return ProviderApi.getModelTypeList(provider.provider)
    .then((options) => {
      modelTypeOptions.value = options
    })
    .finally(() => {
      optionLoading.value = false
    })
}

function open(provider: ModelProviderItem) {
  visible.value = true
  loadModelTypes(provider)
}

function handleProviderSelect(provider: ModelProviderItem) {
  loadModelTypes(provider)
}

function handleModelTypeChange() {
  modelForm.model_name = ''
  modelForm.credential = {}
  baseModelOptions.value = []
  credentialFields.value = []
  modelParamsForm.value = []
  if (!modelForm.model_type) return

  optionLoading.value = true
  ProviderApi.getBaseModelList(modelForm.provider, modelForm.model_type)
    .then((options) => {
      baseModelOptions.value = options
    })
    .finally(() => {
      optionLoading.value = false
    })
}

function handleBaseModelChange() {
  modelForm.credential = {}
  credentialFields.value = []
  modelParamsForm.value = []
  if (!modelForm.model_name) return

  optionLoading.value = true
  Promise.all([
    ProviderApi.getModelCreateForm(modelForm.provider, modelForm.model_type, modelForm.model_name),
    ProviderApi.getBaseModelParamsForm(
      modelForm.provider,
      modelForm.model_type,
      modelForm.model_name,
    ),
  ])
    .then(([fields, paramsForm]) => {
      credentialFields.value = fields
      modelParamsForm.value = paramsForm
      modelForm.credential = Object.fromEntries(
        fields.map((field) => [field.field, field.default_value ?? '']),
      )
      nextTick(() => formRef.value?.clearValidate())
    })
    .finally(() => {
      optionLoading.value = false
    })
}

function handleBack() {
  visible.value = false
  emit('back')
}

function handleSubmit() {
  formRef.value?.validate((valid) => {
    if (!valid) return

    loading.value = true
    ModelApi.postModel({
      ...modelForm,
      model_params_form: modelParamsForm.value,
    })
      .then(() => {
        MsgSuccess('创建成功')
        visible.value = false
        emit('refresh')
      })
      .finally(() => {
        loading.value = false
      })
  })
}

defineExpose({ open })
</script>

<template>
  <MkDrawer
    v-model="visible"
    content-class="h-full p-0!"
    direction="btt"
    title="添加模型"
    @closed="resetData"
  >
    <template #header>
      <div class="flex w-full">
        <h4>添加模型</h4>
        <el-steps :active="1" finish-status="success" class="absolute-center w-75!">
          <el-step title="选择供应商" />
          <el-step title="添加模型" />
        </el-steps>
      </div>
    </template>

    <MkViewLayout :loading="optionLoading" :title="selectedProvider?.name ?? ''">
      <template #aside="{ Header }">
        <component :is="Header">
          <el-select model-value="all" class="w-full">
            <el-option label="全部模型" value="all" />
          </el-select>
        </component>

        <el-scrollbar class="min-h-0 flex-1 px-4 pb-4">
          <MkListItem
            v-for="provider in providers"
            :key="provider.provider"
            class="mb-1"
            :active="selectedProvider?.provider === provider.provider"
            @click="handleProviderSelect(provider)"
          >
            <span class="h-6 w-6 shrink-0" :innerHTML="provider.icon" />
            <span class="ml-3 min-w-0 flex-1 truncate" :title="provider.name">
              {{ provider.name }}
            </span>
          </MkListItem>
        </el-scrollbar>
      </template>

      <template #default="{ Header }">
        <component :is="Header">
          <h4>{{ selectedProvider?.name }}</h4>
        </component>
        <div class="mx-auto w-full max-w-200 pt-4">
          <el-form
            ref="formRef"
            :model="modelForm"
            :rules="formRules"
            label-position="top"
            require-asterisk-position="right"
            @submit.prevent
          >
            <el-form-item prop="name">
              <template #label>
                <span class="inline-flex items-center gap-1">
                  模型名称
                  <el-tooltip content="用于在 MaxKB 中识别该模型" placement="top">
                    <MkIcon :icon="InfoFilled" class="text-N600" />
                  </el-tooltip>
                </span>
              </template>
              <el-input
                v-model="modelForm.name"
                maxlength="64"
                placeholder="请给基础模型设置一个名称"
                @blur="modelForm.name = modelForm.name.trim()"
              />
            </el-form-item>

            <el-form-item label="模型类型" prop="model_type">
              <el-select
                v-model="modelForm.model_type"
                class="w-full"
                placeholder="请选择模型类型"
                @change="handleModelTypeChange"
              >
                <el-option
                  v-for="option in modelTypeOptions"
                  :key="option.value"
                  :label="option.key"
                  :value="option.value"
                />
              </el-select>
            </el-form-item>

            <el-form-item prop="model_name">
              <template #label>
                <span>
                  基础模型
                  <span class="ml-2 font-normal text-warning">
                    列表中未列出的模型，直接输入模型名称，回车即可添加
                  </span>
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
                <el-option
                  v-for="option in baseModelOptions"
                  :key="option.name"
                  :label="option.name"
                  :value="option.name"
                />
              </el-select>
            </el-form-item>

            <template v-for="field in credentialFields" :key="field.field"> </template>
          </el-form>
        </div>
      </template>
    </MkViewLayout>

    <template #footer>
      <el-button :disabled="loading" @click="visible = false">取消</el-button>
      <el-button :disabled="loading" @click="handleBack">上一步</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">保存</el-button>
    </template>
  </MkDrawer>
</template>
