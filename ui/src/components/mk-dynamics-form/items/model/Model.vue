<script setup lang="ts">
import { computed, provide, ref, watch } from 'vue'
import { cloneDeep } from 'lodash'
import { MODEL_STATUS } from '@/api/enums'
import type { Dict, ModelConfig, ModelItem } from '@/api/types'
import type { FormField } from '../../type'
import { providerList } from './provider-data'
import SelectModel from '@/components/business/select-model/index.vue'

defineOptions({ name: 'DynamicFormModel', inheritAttrs: false })

interface ConfiguredModelOption {
  model_id: string
  model_name: string
  provider: string
  model_params_setting?: Dict<unknown>
  /** 配置字段时保存的模型参数表单，运行时据此编辑参数，不再请求接口。 */
  model_form_field?: FormField[]
  status?: ModelItem['status']
  source?: ModelItem['source']
}

const props = withDefaults(defineProps<{ modelValue?: ModelConfig | null; formField: FormField }>(), {
  modelValue: null,
})

const emit = defineEmits<{
  'update:modelValue': [value: ModelConfig]
  change: [field: FormField]
}>()

// 将动态表单保存的模型快照转换为 SelectModel 的扁平选项。
const configuredModels = computed<ConfiguredModelOption[]>(() => props.formField.attrs?.provider_list ?? [])
const modelOptions = computed<ModelItem[]>(() =>
  configuredModels.value.map((model) => ({
    id: model.model_id,
    name: model.model_name,
    model_name: model.model_name,
    model_type: props.formField.model_type ?? '',
    provider: model.provider,
    status: model.status ?? MODEL_STATUS.SUCCESS,
    source: model.source,
  })),
)

// 模型参数：参数表单取自配置快照，默认值使用配置时保存的参数。
const canEditParams = computed(() => configuredModels.value.some((model) => model.model_form_field?.length))

function getModelParamsForm(modelId: string) {
  const selectedModel = configuredModels.value.find((model) => model.model_id === modelId)
  const settings = selectedModel?.model_params_setting ?? {}
  return Promise.resolve(
    (selectedModel?.model_form_field ?? []).map((field) =>
      Object.prototype.hasOwnProperty.call(settings, field.field) ? { ...field, default_value: cloneDeep(settings[field.field]) } : field,
    ),
  )
}
provide('getModelParamsForm', getModelParamsForm)

// SelectModel 切换模型后同步回写参数，此时 Props 尚未更新，记录当前选中的模型
const currentModelId = ref(props.modelValue?.model_id ?? '')
watch(
  () => props.modelValue?.model_id,
  (modelId) => {
    currentModelId.value = modelId ?? ''
  },
)

function handleModelParamsChange(settings: Dict<unknown>) {
  if (!currentModelId.value) return
  emit('update:modelValue', { model_id: currentModelId.value, model_params_setting: settings })
  emit('change', props.formField)
}

function handleModelChange(modelId: string) {
  currentModelId.value = modelId
  const selectedModel = configuredModels.value.find((model) => model.model_id === modelId)
  emit('update:modelValue', {
    model_id: modelId,
    model_params_setting: cloneDeep(selectedModel?.model_params_setting ?? {}),
  })
  emit('change', props.formField)
}
</script>

<template>
  <SelectModel
    v-bind="$attrs"
    :model-value="props.modelValue?.model_id ?? ''"
    :model-params="props.modelValue?.model_params_setting ?? {}"
    :can-edit-params="canEditParams"
    :options="modelOptions"
    :provider-options="providerList"
    @update:model-value="handleModelChange"
    @update:model-params="handleModelParamsChange"
  />
</template>
