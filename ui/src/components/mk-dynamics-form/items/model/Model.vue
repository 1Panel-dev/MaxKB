<script setup lang="ts">
import { computed } from 'vue'
import { cloneDeep } from 'lodash'
import { MODEL_STATUS } from '@/api/enums'
import type { Dict, ModelConfig, ModelItem } from '@/api/types'
import type { FormField } from '../../type'
import { providerList } from './provider-data'
import ModelSelect from '@/components/business/model-select/index.vue'

defineOptions({ name: 'DynamicFormModel', inheritAttrs: false })

interface ConfiguredModelOption {
  model_id: string
  model_name: string
  provider: string
  model_params_setting?: Dict<unknown>
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

// 将动态表单保存的模型快照转换为 ModelSelect 的扁平选项。
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

function handleModelChange(modelId: string) {
  const selectedModel = configuredModels.value.find((model) => model.model_id === modelId)
  emit('update:modelValue', {
    model_id: modelId,
    model_params_setting: cloneDeep(selectedModel?.model_params_setting ?? {}),
  })
  emit('change', props.formField)
}
</script>

<template>
  <!-- // TODO  -->
  <ModelSelect
    v-bind="$attrs"
    :model-value="props.modelValue?.model_id ?? ''"
    :options="modelOptions"
    :provider-options="providerList"
    @update:model-value="handleModelChange"
  />
</template>
