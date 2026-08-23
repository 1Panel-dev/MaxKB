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

  credentialFields.value.forEach((field) => {
    if (field.required) {
      rules[`credential.${field.field}`] = [
        { required: true, message: `请输入${getFieldLabel(field)}`, trigger: 'blur' },
      ]
    }
  })
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
  resetData()
  visible.value = true
  loadModelTypes(provider)
}

function close() {
  visible.value = false
  resetData()
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

function getFieldLabel(field: DynamicFormField) {
  return typeof field.label === 'string' ? field.label : field.label.label
}

function getFieldTooltip(field: DynamicFormField) {
  return typeof field.label === 'string' ? '' : field.label.attrs?.tooltip
}

function getFieldAttrs(field: DynamicFormField) {
  return field.attrs ?? {}
}

function getOptionLabel(field: DynamicFormField, option: Record<string, unknown>) {
  return String(option[field.text_field ?? 'label'] ?? '')
}

function getOptionValue(field: DynamicFormField, option: Record<string, unknown>) {
  return option[field.value_field ?? 'value']
}

function isFieldVisible(field: DynamicFormField) {
  const relations = field.relation_show_field_dict ?? {}
  return Object.entries(relations).every(([key, values]) =>
    values.includes(modelForm.credential[key]),
  )
}

function handleBack() {
  close()
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
        close()
        emit('refresh')
      })
      .finally(() => {
        loading.value = false
      })
  })
}

defineExpose({ open, close })
</script>

<template>
  <MkDrawer
    v-model="visible"
    class="create-model-form-drawer"
    direction="btt"
    size="calc(100% - 68px)"
    title="添加模型"
    @closed="resetData"
  >
    <template #header>
      <div class="grid w-full grid-cols-[1fr_460px_1fr] items-center pr-8">
        <h4>添加模型</h4>
        <el-steps :active="1" align-center finish-status="success">
          <el-step title="选择供应商" />
          <el-step title="添加模型" />
        </el-steps>
      </div>
    </template>

    <div class="flex h-full min-h-0">
      <aside class="flex w-[332px] shrink-0 flex-col border-r border-N900/10 p-5">
        <el-select model-value="all" class="mb-3 w-full">
          <el-option label="全部模型" value="all" />
        </el-select>
        <el-scrollbar class="min-h-0 flex-1">
          <button
            v-for="provider in providers"
            :key="provider.provider"
            type="button"
            class="mb-1 flex h-14 w-full cursor-pointer items-center rounded-md px-3 text-left hover:bg-N900/5"
            :class="{
              'bg-primary/10 text-primary': selectedProvider?.provider === provider.provider,
            }"
            @click="handleProviderSelect(provider)"
          >
            <span class="h-6 w-6 shrink-0" :innerHTML="provider.icon" />
            <span class="ml-3 truncate" :title="provider.name">{{ provider.name }}</span>
          </button>
        </el-scrollbar>
      </aside>

      <main class="flex min-w-0 flex-1 flex-col">
        <div class="border-b border-N900/10 px-8 py-6">
          <h4>{{ selectedProvider?.name }}</h4>
        </div>
        <el-scrollbar v-loading="optionLoading" class="min-h-0 flex-1">
          <el-form
            ref="formRef"
            :model="modelForm"
            :rules="formRules"
            class="mx-auto max-w-[1110px] px-8 py-8"
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

            <template v-for="field in credentialFields" :key="field.field">
              <el-form-item v-if="isFieldVisible(field)" :prop="`credential.${field.field}`">
                <template #label>
                  <span class="inline-flex items-center gap-1">
                    {{ getFieldLabel(field) }}
                    <el-tooltip v-if="getFieldTooltip(field)" :content="getFieldTooltip(field)">
                      <MkIcon :icon="InfoFilled" class="text-N600" />
                    </el-tooltip>
                  </span>
                </template>

                <el-switch
                  v-if="field.input_type === 'SwitchInput'"
                  v-model="modelForm.credential[field.field]"
                  v-bind="getFieldAttrs(field)"
                />
                <el-slider
                  v-else-if="field.input_type === 'Slider'"
                  v-model="modelForm.credential[field.field] as number"
                  v-bind="getFieldAttrs(field)"
                />
                <el-select
                  v-else-if="field.option_list?.length"
                  v-model="modelForm.credential[field.field]"
                  class="w-full"
                  v-bind="getFieldAttrs(field)"
                >
                  <el-option
                    v-for="(option, index) in field.option_list"
                    :key="index"
                    :label="getOptionLabel(field, option)"
                    :value="getOptionValue(field, option)"
                  />
                </el-select>
                <el-input
                  v-else
                  v-model="modelForm.credential[field.field] as string"
                  :show-password="field.input_type === 'PasswordInput'"
                  :type="
                    field.input_type === 'PasswordInput'
                      ? 'password'
                      : field.input_type === 'JsonInput'
                        ? 'textarea'
                        : 'text'
                  "
                  v-bind="getFieldAttrs(field)"
                />
              </el-form-item>
            </template>
          </el-form>
        </el-scrollbar>
      </main>
    </div>

    <template #footer>
      <el-button :disabled="loading" @click="close">取消</el-button>
      <el-button :disabled="loading" @click="handleBack">上一步</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">保存</el-button>
    </template>
  </MkDrawer>
</template>

<style scoped lang="scss">
:deep(.create-model-form-drawer .el-drawer__body .p-6) {
  height: 100%;
  padding: 0;
}

:deep(.create-model-form-drawer .el-drawer__footer),
:deep(.create-model-form-drawer .el-drawer__header) {
  border-color: var(--el-border-color-lighter);
  border-style: solid;
  margin-bottom: 0;
  padding: calc(var(--spacing) * 4) calc(var(--spacing) * 6);
}

:deep(.create-model-form-drawer .el-drawer__footer) {
  border-top-width: 1px;
}

:deep(.create-model-form-drawer .el-drawer__header) {
  border-bottom-width: 1px;
}
</style>
