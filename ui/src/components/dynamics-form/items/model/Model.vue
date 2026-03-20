<template>
  <div class="flex-between w-full">
    <el-select
      :model-value="model_value?.model_id"
      @change="handleModelChange"
      v-bind="$attrs"
      popper-class="select-model"
    >
      <el-option-group
        v-for="(modelList, providerName) in groupedOptions"
        :key="providerName"
        :label="relatedObject(providerList, providerName, 'provider')?.name"
      >
        <el-option
          v-for="item in modelList"
          :key="item.model_id"
          :label="item.model_name"
          :value="item.model_id"
        >
          <div class="flex">
            <span
              v-html="relatedObject(providerList, providerName, 'provider')?.icon"
              class="model-icon mr-8"
            >
            </span>
            <span>{{ item.model_name }}</span>
          </div>
        </el-option>
      </el-option-group>
    </el-select>
    <div class="ml-4">
      <el-button @click="openParamSetting" :disabled="!model_value?.model_id">
        <el-icon>
          <Operation />
        </el-icon>
      </el-button>
    </div>
  </div>
  <AIModeParamSettingDialog ref="AIModeParamSettingDialogRef" @refresh="handleParamRefresh" />
</template>
<script setup lang="ts">
import { ref, computed } from 'vue'
import { groupBy } from 'lodash'
import { relatedObject } from '@/utils/array'
import type { FormField } from '../../type'
import { providerList } from './provider-data'
import AIModeParamSettingDialog from '@/views/application/component/AIModeParamSettingDialog.vue'

const props = withDefaults(
  defineProps<{
    modelValue?: { model_id: string; model_params_setting: Record<string, any> } | null
    formField: FormField
  }>(),
  {
    modelValue: null,
  },
)

const emit = defineEmits(['update:modelValue', 'change'])

const model_value = computed({
  get: () => props.modelValue,
  set: (value) => {
    emit('update:modelValue', value)
    emit('change', props.formField)
  },
})

const groupedOptions = computed(() => {
  const list = (props.formField.attrs?.provider_list as any[]) || []
  return groupBy(list, 'provider')
})

const AIModeParamSettingDialogRef = ref<InstanceType<typeof AIModeParamSettingDialog>>()

function openParamSetting() {
  if (!model_value.value?.model_id) return

  const model_form_field =
    props.formField.attrs?.provider_list.find(
      (p: any) => p.model_id === model_value.value?.model_id,
    ).model_form_field || []

  AIModeParamSettingDialogRef.value?.open(
    model_value.value.model_id,
    undefined,
    model_value.value.model_params_setting,
    model_form_field,
  )
}

function handleParamRefresh(paramData: any) {
  if (model_value.value) {
    model_value.value = {
      ...model_value.value,
      model_params_setting: paramData,
    }
  }
}

const handleModelChange = (selectedId: string) => {
  const list = (props.formField.attrs?.provider_list as any[]) || []
  const selectedItem = list.find((p) => p.model_id === selectedId)
  model_value.value = {
    model_id: selectedId,
    model_params_setting: selectedItem?.model_params_setting || {},
  }
}
</script>
<style lang="scss" scoped>
// AI模型选择：添加模型hover样式
.select-model {
  .el-select-dropdown__footer {
    &:hover {
      background-color: var(--el-fill-color-light);
    }
  }

  .model-icon {
    width: 18px;
  }

  .check-icon {
    position: absolute;
    right: 10px;
  }
}
</style>
