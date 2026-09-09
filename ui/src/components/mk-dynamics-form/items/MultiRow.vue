<script setup lang="ts">
import type { DynamicFormValue } from '../type'
import { computed } from 'vue'
import type { FormField } from '@/components/mk-dynamics-form/type'
import type { CheckboxValueType } from 'element-plus'
const props = defineProps<{
  formValue?: DynamicFormValue
  formfieldList?: FormField[]
  field: string
  otherParams: DynamicFormValue
  formField: FormField
  view?: boolean
  // 选中的值
  modelValue?: DynamicFormValue
}>()
const emit = defineEmits<{ 'update:modelValue': [value: CheckboxValueType[]] }>()

// 兼容旧配置的空字符串；新增选择时沿用原有逻辑，清理已不在选项中的值。
const selectedValues = computed<CheckboxValueType[]>({
  get: () => (Array.isArray(props.modelValue) ? props.modelValue : []),
  set: (values) => {
    emit('update:modelValue', values.length > selectedValues.value.length ? values.filter((value) => optionValues.value.includes(value)) : values)
  },
})

const textField = computed(() => {
  return props.formField.text_field ? props.formField.text_field : 'key'
})

const valueField = computed(() => {
  return props.formField.value_field ? props.formField.value_field : 'value'
})
const optionValues = computed(() => {
  return options.value.map((item) => item[valueField.value])
})
const options = computed(() => {
  return props.formField.option_list ? props.formField.option_list : []
})
</script>

<template>
  <el-checkbox-group v-model="selectedValues">
    <el-checkbox-button v-for="option in options" :key="option[valueField]" :value="option[valueField]">
      {{ option[textField] }}
    </el-checkbox-button>
  </el-checkbox-group>
</template>
