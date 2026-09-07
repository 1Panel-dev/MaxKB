<script setup lang="ts">
import type { DynamicFormValue } from '../../type'
import { computed, inject, ref } from 'vue'
import SelectModel from '@/components/business/select-model/index.vue'
import { providerList as providerOptions } from '../../items/model/provider-data'
import { MODEL_TYPE_LABELS } from '@/constants/model'
const getSelectModelList = inject<(params: { model_type: string }) => Promise<DynamicFormValue>>('getSelectModelList')
const getModelParamsForm = inject<(modelId: string) => Promise<DynamicFormValue>>('getModelParamsForm')

const props = defineProps<{ modelValue: DynamicFormValue }>()

const emit = defineEmits(['update:modelValue'])

const formValue = computed({
  set: (item: DynamicFormValue) => {
    emit('update:modelValue', item)
  },
  get: () => {
    return props.modelValue
  },
})

const selectedIds = computed({
  get: () => (formValue.value.provider_list || []).map((p: DynamicFormValue) => p.model_id),
  set: (newIds: string[]) => {
    const oldList = formValue.value.provider_list || []
    const newList = newIds.map((id: string) => {
      const existing = oldList.find((p: DynamicFormValue) => p.model_id === id)
      return existing || { model_id: id, model_params_setting: {} }
    })
    formValue.value.provider_list = newList

    const currentId = formValue.value.default_value?.model_id
    if (currentId && !newIds.includes(currentId)) {
      formValue.value.default_value = {}
    }

    // find new model then get it default value
    const oldIds = oldList.map((p: DynamicFormValue) => p.model_id)
    const addedIds = newIds.filter((id: string) => !oldIds.includes(id))
    addedIds.forEach((id: string) => {
      fetchDefaultParams(id)
    })
  },
})

const selectedModelsOptions = computed(() => {
  const ids = (formValue.value.provider_list || []).map((p: DynamicFormValue) => p.model_id)
  return rawModelOptions.value.filter((model: DynamicFormValue) => ids.includes(model.id))
})

function fetchDefaultParams(modelId: string) {
  if (!getModelParamsForm) return
  getModelParamsForm(modelId).then((res: DynamicFormValue) => {
    const formFields = res?.data || []
    const defaults = (res?.data || [])
      .map((item: DynamicFormValue) => {
        if (item.show_default_value === false) {
          return { [item.field]: undefined }
        } else {
          return { [item.field]: item.default_value }
        }
      })
      .reduce((x: DynamicFormValue, y: DynamicFormValue) => ({ ...x, ...y }), {})
    // update to model_params_setting
    const target = formValue.value.provider_list.find((p: DynamicFormValue) => p.model_id === modelId)
    if (target) {
      target.model_params_setting = defaults
      target.model_form_field = formFields
    }
  })
}
const rawModelOptions = ref<DynamicFormValue[]>([])

const fetchModelByType = (type: string) => {
  if (!type || !getSelectModelList) return
  getSelectModelList({ model_type: type }).then((res: DynamicFormValue) => {
    rawModelOptions.value = res
  })
}

const handleModelTypeChange = (val: string) => {
  formValue.value.provider_list = []
  formValue.value.default_value = {}

  if (val) {
    fetchModelByType(val)
  } else {
    rawModelOptions.value = []
  }
}

const getModelInfo = (modelId: string) => {
  return rawModelOptions.value.find((item: DynamicFormValue) => item.id === modelId)
}

// default_value 赋值
const getProviderItem = (modelId: string) => {
  const found = formValue.value.provider_list.find((p: DynamicFormValue) => p.model_id === modelId)
  if (found) {
    const rest = { ...found }
    delete rest.model_form_field
    return rest
  }
  return { model_id: modelId, model_params_setting: {} }
}

const defaultModelId = computed({
  get: () => formValue.value.default_value?.model_id ?? '',
  set: (modelId: string) => {
    formValue.value.default_value = modelId ? getProviderItem(modelId) : {}
  },
})

const getData = () => {
  const providerList = (formValue.value.provider_list || []).map((p: DynamicFormValue) => {
    const modelInfo = getModelInfo(p.model_id)
    return {
      model_id: p.model_id,
      model_name: modelInfo?.name || '',
      provider: modelInfo?.provider || '',
      model_params_setting: p.model_params_setting || {},
      model_form_field: p.model_form_field || [],
    }
  })
  return {
    input_type: 'Model',
    model_type: formValue.value.model_type,
    default_value: formValue.value.default_value,
    attrs: { provider_list: providerList },
  }
}

const render = (formData: DynamicFormValue) => {
  formValue.value.model_type = formData.model_type
  formValue.value.provider_list = formData.attrs?.provider_list || []
  formValue.value.default_value = formData.default_value || {}

  if (formData.model_type) {
    fetchModelByType(formData.model_type)
  }
}

defineExpose({ getData, render })
</script>

<template>
  <el-form-item label="模型类型" required prop="model_type" :rules="[{ required: true, message: '请选择模型类型' }]">
    <el-select v-model="formValue.model_type" placeholder="请选择模型类型" @change="handleModelTypeChange">
      <el-option v-for="(label, value) in MODEL_TYPE_LABELS" :key="value" :label="label" :value="value" />
    </el-select>
  </el-form-item>

  <el-form-item label="可选模型" required prop="provider_list" :rules="[{ required: true, message: '请选择模型', type: 'array' }]">
    <!-- // TODO  -->
    <SelectModel
      multiple
      v-model="selectedIds"
      placeholder="请选择模型"
      :options="rawModelOptions"
      :provider-options="providerOptions"
      :model-type="formValue.model_type"
    >
    </SelectModel>
  </el-form-item>
  <el-form-item
    label="默认模型"
    prop="default_value.model_id"
    :required="formValue.required"
    :rules="formValue.required ? [{ required: true, message: '请选择模型' }] : []"
    v-if="formValue.provider_list && formValue.provider_list.length > 0"
  >
    <!-- // TODO  -->
    <SelectModel v-model="defaultModelId" placeholder="请选择模型" :options="selectedModelsOptions" :provider-options="providerOptions" />
  </el-form-item>
</template>
