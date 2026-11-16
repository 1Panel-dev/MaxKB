<script setup lang="ts">
import { useI18n } from 'vue-i18n'
import type { DynamicFormValue } from '../../type'
import { computed, onMounted, watch } from 'vue'

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
watch(
  () => formValue.value.minlength,
  () => {
    if (formValue.value.minlength > formValue.value.maxlength) {
      formValue.value.maxlength = formValue.value.minlength
    }
  },
)
const getData = () => {
  return {
    input_type: 'PasswordInput',
    attrs: {
      maxlength: formValue.value.maxlength,
      minlength: formValue.value.minlength,
      'show-word-limit': true,
      type: 'password',
      'show-password': true,
    },
    default_value: formValue.value.default_value,
    show_default_value: formValue.value.show_default_value,
    props_info: {
      rules: formValue.value.required
        ? [
            { required: true, message: t('common.form.inputFieldSpaced', { fieldName: formValue.value.label }) },
            {
              min: formValue.value.minlength,
              max: formValue.value.maxlength,
              message: t('dynamicForm.validation.fieldLengthRange', {
                fieldName: formValue.value.label,
                min: formValue.value.minlength,
                max: formValue.value.maxlength,
              }),
              trigger: 'blur',
            },
          ]
        : [
            {
              min: formValue.value.minlength,
              max: formValue.value.maxlength,
              message: t('dynamicForm.validation.fieldLengthRange', {
                fieldName: formValue.value.label,
                min: formValue.value.minlength,
                max: formValue.value.maxlength,
              }),
              trigger: 'blur',
            },
          ],
    },
  }
}
const render = (formData: DynamicFormValue) => {
  const attrs = formData.attrs || {}
  formValue.value.minlength = attrs.minlength
  formValue.value.maxlength = attrs.maxlength
  formValue.value.default_value = formData.default_value
  formValue.value.show_default_value = formData.show_default_value
  formValue.value.show_password = attrs['show-password']
}
const rules = computed(() => [
  {
    min: formValue.value.minlength,
    max: formValue.value.maxlength,
    message: t('dynamicForm.validation.lengthRange', { min: formValue.value.minlength, max: formValue.value.maxlength }),
    trigger: 'blur',
  },
])

defineExpose({ getData, render })
onMounted(() => {
  formValue.value.minlength = 0
  formValue.value.maxlength = 200
  formValue.value.default_value = ''
  formValue.value.show_password = true

  if (formValue.value.show_default_value === undefined) {
    formValue.value.show_default_value = true
  }
})
</script>

<template>
  <div class="mk-required mb-2">{{ t('dynamicForm.text.length') }}</div>
  <div class="flex w-full items-start gap-2">
    <el-form-item
      class="min-w-0 flex-1"
      :rules="[{ required: true, message: t('dynamicForm.text.minLengthRequired'), trigger: 'change' }]"
      prop="minlength"
    >
      <el-input-number v-model="formValue.minlength" :min="1" :step="1" controls-position="right" align="left" step-strictly />
    </el-form-item>
    <span class="flex-center shrink-0 h-8">-</span>
    <el-form-item
      class="min-w-0 flex-1"
      :rules="[{ required: true, message: t('dynamicForm.text.maxLengthRequired'), trigger: 'change' }]"
      prop="maxlength"
    >
      <el-input-number
        v-model="formValue.maxlength"
        :min="formValue.minlength > formValue.maxlength ? formValue.minlength : 1"
        :step="1"
        controls-position="right"
        align="left"
        step-strictly
      />
    </el-form-item>
  </div>

  <el-form-item
    class="mk-hide-asterisk"
    :required="formValue.required"
    prop="default_value"
    :rules="
      formValue.required
        ? [{ required: true, message: t('common.form.inputField', { fieldName: t('dynamicForm.fields.defaultValue') }) }, ...rules]
        : rules
    "
  >
    <template #label>
      <div class="flex-between">
        <span :class="formValue.required ? 'mk-required' : ''">{{ t('dynamicForm.fields.defaultValue') }}</span>
        <el-checkbox v-model="formValue.show_default_value" :label="t('dynamicForm.defaultValue.show')" />
      </div>
    </template>

    <el-input
      v-model="formValue.default_value"
      :maxlength="formValue.maxlength"
      :minlength="formValue.minlength"
      :placeholder="t('common.form.inputField', { fieldName: t('dynamicForm.fields.defaultValue') })"
      show-word-limit
      type="password"
      show-password
    />
  </el-form-item>
</template>
<style lang="scss" scoped></style>
