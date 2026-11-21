<script setup lang="ts">
import { computed, onBeforeMount, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { DynamicFormValidatorCallback, DynamicFormValue } from '../../type'
const { t } = useI18n({ useScope: 'global' })

const props = defineProps<{ modelValue: DynamicFormValue }>()
const emit = defineEmits(['update:modelValue'])
const formValue = computed({
  set: (item) => {
    emit('update:modelValue', item)
  },
  get: () => {
    return props.modelValue
  },
})

const getData = () => {
  return {
    input_type: 'Slider',
    attrs: {
      min: formValue.value.min,
      max: formValue.value.max,
      step: formValue.value.step,
      precision: formValue.value.precision,
      'show-input-controls': true,
      'show-input': formValue.value.showInput,
    },
    props_info: {
      rules: [
        { message: t('common.validation.inputFieldRequired', { label: formValue.value.label }), trigger: 'blur', required: formValue.value.required },
      ],
    },
    show_default_value: true,
    default_value: formValue.value.default_value,
  }
}
watch(
  () => formValue.value.min,
  () => {
    if (formValue.value.min > formValue.value.max) {
      formValue.value.max = formValue.value.min
    }
  },
)
const render = (formData: DynamicFormValue) => {
  const attrs = formData.attrs
  formValue.value.option_list = formData.option_list
  formValue.value.min = attrs.min
  formValue.value.max = attrs.max
  formValue.value.step = attrs.step
  formValue.value.showInput = attrs['show-input']
  formValue.value.default_value = formData.default_value
}
const stepRules = [
  {
    required: true,
    validator: (_rule: unknown, value: DynamicFormValue, callback: DynamicFormValidatorCallback) => {
      if (value === 0) {
        callback(new Error(t('dynamicForm.fields.step.invalidMessage')))
        return false
      }
      if (!value) {
        callback(new Error(t('dynamicForm.fields.step.requiredMessage')))
        return false
      }

      return true
    },
    trigger: 'blur',
  },
]
defineExpose({ getData, render })
onBeforeMount(() => {
  formValue.value.min = 0
  formValue.value.max = 20
  formValue.value.step = 0.1
  formValue.value.default_value = 1
  formValue.value.showInput = true
})
</script>

<template>
  <el-form-item :label="t('dynamicForm.fields.showInput.label')" required prop="showInput" @click.prevent>
    <el-switch v-model="formValue.showInput" />
  </el-form-item>
  <!-- 取值范围 -->
  <div class="mk-required mb-2">{{ t('dynamicForm.labels.range') }}</div>
  <div class="flex w-full items-start gap-2">
    <el-form-item
      class="min-w-0 flex-1"
      :rules="[{ required: true, message: t('dynamicForm.fields.min.requiredMessage'), trigger: 'change' }]"
      prop="min"
    >
      <el-input-number v-model="formValue.min" controls-position="right" align="left" />
    </el-form-item>
    <span class="flex-center shrink-0 h-8">-</span>
    <el-form-item
      class="min-w-0 flex-1"
      :rules="[{ required: true, message: t('dynamicForm.fields.max.requiredMessage'), trigger: 'change' }]"
      prop="max"
    >
      <el-input-number
        v-model="formValue.max"
        :min="formValue.min > formValue.max ? formValue.min : undefined"
        controls-position="right"
        align="left"
      />
    </el-form-item>
  </div>

  <el-form-item :label="t('dynamicForm.fields.step.label')" required prop="step" :rules="stepRules">
    <el-input-number v-model="formValue.step" :min="0" controls-position="right" align="left" />
  </el-form-item>

  <el-form-item
    :label="t('dynamicForm.fields.defaultValue.label')"
    :required="formValue.required"
    prop="default_value"
    :rules="formValue.required ? [{ required: true, message: t('dynamicForm.fields.defaultValue.requiredMessage') }] : []"
  >
    <MkSlider
      v-model="formValue.default_value"
      :show-input="formValue.showInput"
      :max="formValue.max"
      :min="formValue.min"
      :step="formValue.step === 0 ? 0.1 : formValue.step"
      :precision="formValue.precision"
    />
  </el-form-item>
</template>
