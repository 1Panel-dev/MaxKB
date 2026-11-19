<script setup lang="ts">
import { computed, nextTick, reactive, ref, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type SystemResourceModelApi from '@/api/admin/system/resource-management/model'
import type SystemSharedModelApi from '@/api/admin/system/shared-resources/model'
import type ModelApi from '@/api/admin/workspace/model'
import type { BaseModelOption, Dict, ModelItem, ModelPayload, ModelProviderItem } from '@/api/types'
import type { DynamicFormValue, FormField } from '@/components/mk-dynamics-form'
import ProviderApi from '@/api/admin/model-provider'
import { MkDynamicsForm } from '@/components/mk-dynamics-form'
import { loadCachedBaseModelOptions, loadCachedOrBuiltinBaseModelOptions } from '@/views/model/base-model-options'
import { MODEL_TYPE_LABELS } from '@/constants/model'
import { MsgSuccess, MsgWarning } from '@/utils/message'

defineOptions({ name: 'EditModelDrawer' })

const { t } = useI18n({ useScope: 'global' })

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
    return true
  }
  return false
}
const baseModelLoading = ref(false)
const credentialFields = ref<FormField[]>([])

const modelForm = reactive<ModelPayload>({ credential: {}, model_name: '', model_type: '', name: '', provider: '' })
let credentialSnapshot = '{}'

const drawerTitle = computed(() => `${t('common.actions.edit')} ${selectedProvider.value?.name ?? ''}`)

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
        loadCachedOrBuiltinBaseModelOptions(detail.provider, detail.model_type, detail.credential as Record<string, unknown>, model.id),
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

async function fetchBaseModelOptions() {
  if (!modelForm.provider || !modelForm.model_type) return
  const requiredFields = credentialFields.value.filter((field) => field.required !== false).map((field) => field.field)
  if (requiredFields.length) {
    const valid = await dynamicsFormRef.value?.ruleFormRef?.validateField(requiredFields).then(
      () => true,
      () => false,
    )
    if (!valid) return
  }
  baseModelLoading.value = true
  const requestProvider = modelForm.provider
  const requestModelType = modelForm.model_type
  const requestCredentialSnapshot = JSON.stringify(modelForm.credential)
  const loadBuiltin = () =>
    ProviderApi.getBaseModelList(requestProvider, requestModelType).then((options) => {
      applyBaseModelOptions(requestProvider, requestModelType, requestCredentialSnapshot, options)
      MsgWarning(t('model.messages.baseModelsFallback'))
    })
  ProviderApi.getBaseModelList(requestProvider, requestModelType, undefined, modelForm.credential as Record<string, unknown>)
    .then((options) => {
      if (options?.length) {
        if (applyBaseModelOptions(requestProvider, requestModelType, requestCredentialSnapshot, options)) {
          MsgSuccess(t('common.messages.fetchSuccess'))
        }
        return
      }
      return loadBuiltin()
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
      void loadCachedBaseModelOptions(modelForm.provider, modelForm.model_type, modelForm.credential as Record<string, unknown>).then((options) =>
        applyBaseModelOptions(modelForm.provider, modelForm.model_type, snapshot, options),
      )
    }, 500)
  },
)

function handleBaseModelChange() {
  // 切换基础模型时保留已填写的凭证参数（同供应商/类型下字段一致，直接沿用）。
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
        MsgSuccess(t('common.messages.updateSuccess'))
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
      <MkDynamicsForm ref="dynamicsFormRef" v-model="modelFormData" :render-data="credentialFields" :validate-on-rule-change="false">
        <template #default>
          <el-form-item
            class="mk-hide-asterisk"
            prop="name"
            :rules="{ whitespace: true, required: true, message: t('model.fields.name.requiredMessage'), trigger: 'blur' }"
          >
            <template #label>
              <span class="inline-flex items-center gap-2">
                <span class="mk-required">{{ t('model.fields.name.label') }}</span>

                <MkTooltip :content="t('model.fields.name.description')" placement="right">
                  <MkIcon name="icon_info_outlined" class="text-N600!"></MkIcon>
                </MkTooltip>
              </span>
            </template>
            <el-input
              v-model="modelForm.name"
              maxlength="64"
              :placeholder="t('model.fields.name.placeholder')"
              @blur="modelForm.name = modelForm.name.trim()"
            />
          </el-form-item>

          <el-form-item
            class="mk-hide-asterisk"
            prop="model_type"
            :rules="{ required: true, message: t('model.fields.type.requiredMessage'), trigger: 'change' }"
          >
            <template #label>
              <span class="inline-flex items-center gap-2">
                <span class="mk-required">{{ t('model.fields.type.label') }}</span>
                <MkTooltip placement="right">
                  <template #content>
                    <p>{{ t('model.types.llm.description') }}</p>
                    <p>{{ t('model.types.embedding.description') }}</p>
                    <p>{{ t('model.types.stt.description') }}</p>
                    <p>{{ t('model.types.tts.description') }}</p>
                    <p>{{ t('model.types.reranker.description') }}</p>
                    <p>{{ t('model.types.image.description') }}</p>
                    <p>{{ t('model.types.tti.description') }}</p>
                    <p>{{ t('model.types.ttv.description') }}</p>
                    <p>{{ t('model.types.itv.description') }}</p>
                  </template>
                  <MkIcon name="icon_info_outlined" class="text-N600!"></MkIcon>
                </MkTooltip>
              </span>
            </template>
            <el-select v-model="modelForm.model_type" class="w-full" disabled :placeholder="t('model.fields.type.placeholder')">
              <el-option v-for="(label, value) in MODEL_TYPE_LABELS" :key="value" :label="label" :value="value" />
            </el-select>
          </el-form-item>
        </template>

        <template #after>
          <el-form-item
            class="mk-hide-asterisk"
            prop="model_name"
            :rules="{ required: true, message: t('model.fields.baseModel.requiredMessage'), trigger: 'change' }"
          >
            <template #label>
              <span class="inline-flex w-full items-center gap-2">
                <span class="inline-flex items-center gap-2">
                  <span class="mk-required">{{ t('model.fields.baseModel.label') }}</span>
                  <span class="text-warning">{{ t('model.fields.baseModel.description') }}</span>
                </span>
                <el-button
                  class="ml-auto"
                  link
                  type="primary"
                  :disabled="!modelForm.provider || !modelForm.model_type"
                  :loading="baseModelLoading"
                  @click="fetchBaseModelOptions()"
                >
                  <MkIcon name="icon_refresh_outlined" class="mr-1"></MkIcon>
                  {{ t('model.actions.fetchModels') }}
                </el-button>
              </span>
            </template>
            <el-select
              v-model="modelForm.model_name"
              allow-create
              class="w-full"
              default-first-option
              filterable
              :loading="baseModelLoading"
              :placeholder="t('model.fields.baseModel.placeholder')"
              @change="handleBaseModelChange"
            >
              <el-option v-for="option in baseModelOptions" :key="option.name" :label="option.name" :value="option.name">
                <template #default>
                  <div class="flex-align-center gap-2">
                    <span>{{ option.name }}</span>
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
      <el-button plain :disabled="loading" @click="visible = false">{{ t('common.actions.cancel') }}</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">{{ t('common.actions.save') }}</el-button>
    </template>
  </MkDrawer>
</template>
