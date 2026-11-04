<script setup lang="ts">
import { computed, nextTick, reactive, ref, watch } from 'vue'
import type ModelApi from '@/api/admin/workspace/model'
import type SystemResourceModelApi from '@/api/admin/system/resource-management/model'
import type SystemSharedModelApi from '@/api/admin/system/shared-resources/model'
import type { BaseModelOption, Dict, ModelItem, ModelPayload, ModelProviderItem } from '@/api/types'
import ProviderApi from '@/api/admin/model-provider'
import { MkDynamicsForm, type DynamicFormValue, type FormField } from '@/components/mk-dynamics-form'
import { MODEL_TYPE_LABELS } from '@/constants'
import { loadCachedBaseModelOptions, loadCachedOrBuiltinBaseModelOptions } from '@/views/model/base-model-options'
import { MsgSuccess, MsgWarning } from '@/utils/message'

defineOptions({ name: 'EditModelDrawer' })

const props = defineProps<{ api: typeof ModelApi | typeof SystemSharedModelApi | typeof SystemResourceModelApi }>()

const emit = defineEmits<{ closed: []; refresh: [] }>()

type ModelDetail = ModelItem & Pick<ModelPayload, 'credential'>

const dynamicsFormRef = ref<InstanceType<typeof MkDynamicsForm>>()
const visible = ref(false)
const loading = ref(false)
const formLoading = ref(false)
const selectedProvider = ref<ModelProviderItem>()
const currentModelId = ref('')
const baseModelOptions = ref<BaseModelOption[]>([])
// 仅当响应与当前「供应商 + 类型 + 凭证」一致时才应用，避免过期响应覆盖新列表
function applyBaseModelOptions(provider: string, modelType: string, credentialSnapshot: string, options?: BaseModelOption[]) {
  if (
    options?.length &&
    provider === modelForm.provider &&
    modelType === modelForm.model_type &&
    JSON.stringify(modelForm.credential) === credentialSnapshot
  ) {
    baseModelOptions.value = options
  }
}
const baseModelLoading = ref(false)
const credentialFields = ref<FormField[]>([])

const modelForm = reactive<ModelPayload>({ credential: {}, model_name: '', model_type: '', name: '', provider: '' })
let credentialSnapshot = '{}'

const drawerTitle = computed(() => `编辑 ${selectedProvider.value?.name ?? ''}`)

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

function open(provider: ModelProviderItem, model: ModelItem) {
  resetData()
  selectedProvider.value = provider
  currentModelId.value = model.id
  visible.value = true
  formLoading.value = true

  props.api
    .getModelDetail(model.id)
    .then((response) => {
      const detail = response as ModelDetail
      modelForm.credential = detail.credential ?? {}
      modelForm.model_name = detail.model_name
      modelForm.model_type = detail.model_type
      modelForm.name = detail.name
      modelForm.provider = detail.provider
      credentialSnapshot = JSON.stringify(modelForm.credential)

      return Promise.all([
        loadCachedOrBuiltinBaseModelOptions(
          detail.provider,
          detail.model_type,
          detail.credential as Record<string, unknown>,
          model.id,
        ),
        ProviderApi.getModelCreateForm(detail.provider, detail.model_type, detail.model_name),
      ])
    })
    .then(([baseModels, fields]) => {
      applyBaseModelOptions(modelForm.provider, modelForm.model_type, credentialSnapshot, baseModels)
      credentialFields.value = fields
      return nextTick(() => dynamicsFormRef.value?.render(fields, modelFormData.value))
    })
    .finally(() => {
      formLoading.value = false
    })
}

function fetchBaseModelOptions() {
  if (!modelForm.provider || !modelForm.model_type) return
  baseModelLoading.value = true
  const requestProvider = modelForm.provider
  const requestModelType = modelForm.model_type
  const requestCredentialSnapshot = JSON.stringify(modelForm.credential)
  const loadBuiltin = () =>
    ProviderApi.getBaseModelList(requestProvider, requestModelType).then((options) => {
      applyBaseModelOptions(requestProvider, requestModelType, requestCredentialSnapshot, options)
      MsgWarning('未获取到官方模型列表，已展示内置常用模型')
    })
  ProviderApi.getBaseModelList(requestProvider, requestModelType, undefined, modelForm.credential as Record<string, unknown>)
    .then((options) => {
      if (options?.length) {
        applyBaseModelOptions(requestProvider, requestModelType, requestCredentialSnapshot, options)
      } else {
        return loadBuiltin()
      }
    })
    .catch(() => loadBuiltin())
    .finally(() => {
      baseModelLoading.value = false
    })
}

// 打开抽屉时优先使用后端缓存的基础模型列表，未命中回落内置默认列表。
// 凭证（url/key）变化时尝试命中缓存，命中才刷新列表，避免每次手动获取。
let credentialCacheTimer: ReturnType<typeof setTimeout> | undefined
watch(
  () => JSON.stringify(modelForm.credential),
  () => {
    if (!modelForm.provider || !modelForm.model_type) return
    clearTimeout(credentialCacheTimer)
    credentialCacheTimer = setTimeout(() => {
      const snapshot = JSON.stringify(modelForm.credential)
      void loadCachedBaseModelOptions(
        modelForm.provider,
        modelForm.model_type,
        modelForm.credential as Record<string, unknown>,
      ).then((options) => applyBaseModelOptions(modelForm.provider, modelForm.model_type, snapshot, options))
    }, 500)
  },
)

function handleBaseModelChange() {
  modelForm.credential = {}
  credentialFields.value = []
  void dynamicsFormRef.value?.render([], modelFormData.value)
  if (!modelForm.model_name) return

  formLoading.value = true
  ProviderApi.getModelCreateForm(modelForm.provider, modelForm.model_type, modelForm.model_name)
    .then((fields) => {
      credentialFields.value = fields
      return dynamicsFormRef.value?.render(fields, modelFormData.value)
    })
    .finally(() => {
      formLoading.value = false
    })
}

function handleSubmit() {
  dynamicsFormRef.value?.validate().then(() => {
    loading.value = true
    return props.api
      .putModel(currentModelId.value, modelForm)
      .then(() => {
        MsgSuccess('修改成功')
        visible.value = false
        emit('refresh')
      })
      .finally(() => {
        loading.value = false
      })
  })
}

function resetData() {
  selectedProvider.value = undefined
  currentModelId.value = ''
  modelForm.credential = {}
  modelForm.model_name = ''
  modelForm.model_type = ''
  modelForm.name = ''
  modelForm.provider = ''
  baseModelOptions.value = []
  credentialFields.value = []
  loading.value = false
  formLoading.value = false
}

function handleClosed() {
  resetData()
  emit('closed')
}

defineExpose({ open })
</script>

<template>
  <MkDrawer v-model="visible" :title="drawerTitle" direction="btt" @closed="handleClosed">
    <div v-loading="formLoading" class="mx-auto w-full max-w-200">
      <MkDynamicsForm ref="dynamicsFormRef" v-model="modelFormData" :render-data="credentialFields">
        <template #default>
          <el-form-item
            class="mk-hide-asterisk"
            prop="name"
            :rules="{ whitespace: true, required: true, message: '请输入模型名称', trigger: 'blur' }"
          >
            <template #label>
              <span class="inline-flex items-center gap-2">
                <span class="mk-required"> 模型名称</span>

                <MkTooltip content="MaxKB 中自定义的模型名称" placement="right">
                  <MkIcon name="icon_info_outlined" class="text-N600!"></MkIcon>
                </MkTooltip>
              </span>
            </template>
            <el-input v-model="modelForm.name" maxlength="64" placeholder="请给基础模型设置一个名称" @blur="modelForm.name = modelForm.name.trim()" />
          </el-form-item>

          <el-form-item prop="model_type" label="模型类型" required>
            <el-select v-model="modelForm.model_type" class="w-full" disabled>
              <el-option v-for="(label, value) in MODEL_TYPE_LABELS" :key="value" :label="label" :value="value" />
            </el-select>
          </el-form-item>

          <el-form-item class="mk-hide-asterisk" prop="model_name" :rules="{ required: true, message: '请选择模型类型', trigger: 'change' }">
            <template #label>
              <span class="inline-flex items-center gap-2">
                <span class="mk-required"> 基础模型</span>
                <span class="text-warning"> 列表中未列出的模型，直接输入模型名称，回车即可添加 </span>
                <el-button
                  class="ml-auto"
                  link
                  type="primary"
                  :disabled="!modelForm.provider || !modelForm.model_type"
                  :loading="baseModelLoading"
                  @click="fetchBaseModelOptions()"
                >
                  <MkIcon name="icon_refresh_outlined" class="mr-1"></MkIcon>
                  获取模型
                </el-button>
              </span>
            </template>
            <el-select
              v-model="modelForm.model_name"
              allow-create
              class="w-full"
              default-first-option
              filterable
              placeholder="请先点击「获取模型」加载列表，或直接输入模型名称后回车"
              @change="handleBaseModelChange"
            >
              <el-option v-for="option in baseModelOptions" :key="option.name" :label="option.name" :value="option.name">
                <template #default>
                  <div class="flex-align-center gap-2">
                    <span>{{ option.name }} </span>
                    <MkTooltip v-if="option.desc" :content="option.desc" placement="right">
                      <MkIcon name="icon_info_outlined" class="text-N600!"></MkIcon>
                    </MkTooltip>
                  </div>
                </template>
              </el-option>
            </el-select>
          </el-form-item>
        </template>
      </MkDynamicsForm>
    </div>

    <template #footer>
      <el-button plain :disabled="loading" @click="visible = false">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">保存</el-button>
    </template>
  </MkDrawer>
</template>
