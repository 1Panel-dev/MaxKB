<script setup lang="ts">
import type { DynamicFormValue } from '../../type'
import { computed } from 'vue'
import { groupBy, flatMap } from 'lodash'
import { relatedObject } from '@/utils/common'
import type { FormField } from '../../type'
import { providerList } from './provider-data'

defineOptions({ name: 'DynamicFormModel' })

const props = withDefaults(
  defineProps<{
    modelValue?: {
      model_id: string
      model_params_setting: Record<string, DynamicFormValue>
    } | null
    formField: FormField
  }>(),
  {
    modelValue: null,
  },
)

const emit = defineEmits(['update:modelValue', 'change'])

const modelValueProxy = computed({
  get: () => props.modelValue,
  set: (value) => {
    emit('update:modelValue', value)
    emit('change', props.formField)
  },
})

const groupedOptions = computed(() => {
  const list = (props.formField.attrs?.provider_list as DynamicFormValue[]) || []
  return groupBy(list, 'provider')
})

const getModelProvider = computed(() => {
  return (id: string) => {
    const item = flatMap(groupedOptions.value)?.find(
      (item: DynamicFormValue) => item.model_id === id,
    )
    return (item as DynamicFormValue)?.provider || ''
  }
})

const handleModelChange = (selectedId: string) => {
  const list = (props.formField.attrs?.provider_list as DynamicFormValue[]) || []
  const selectedItem = list.find((p) => p.model_id === selectedId)
  modelValueProxy.value = {
    model_id: selectedId,
    model_params_setting: selectedItem?.model_params_setting || {},
  }
}
</script>

<template>
  <div class="complex-select flex align-center w-full">
    <el-select
      class="complex-select__left"
      :model-value="modelValueProxy?.model_id"
      @change="handleModelChange"
      v-bind="$attrs"
      popper-class="select-model"
    >
      <el-option-group
        v-for="(modelList, providerName) in groupedOptions"
        :key="providerName"
        :label="relatedObject(providerList, String(providerName), 'provider')?.name"
      >
        <el-option
          v-for="item in modelList"
          :key="item.model_id"
          :label="item.model_name"
          :value="item.model_id"
        >
          <el-space :size="8">
            <span
              :innerHTML="
                String(relatedObject(providerList, String(providerName), 'provider')?.icon ?? '')
              "
              class="select-model-icon"
              style="margin-top: -7px"
            >
            </span>
            <span>{{ item.model_name }}</span>
          </el-space>
        </el-option>
      </el-option-group>
      <template #label="{ label, value }">
        <el-space :size="8" v-if="value">
          <span
            class="select-model-icon"
            :innerHTML="
              String(relatedObject(providerList, getModelProvider(value), 'provider')?.icon ?? '')
            "
          >
          </span>
          <span>
            <span>{{ label }}</span>
          </span>
        </el-space>
      </template>
    </el-select>
  </div>
</template>
<style lang="scss" scoped>
// AI模型选择：添加模型hover样式
.select-model {
  .el-select-dropdown__footer {
    &:hover {
      background-color: var(--el-fill-color-light);
    }
  }

  .check-icon {
    position: absolute;
    right: 10px;
  }
}
</style>
