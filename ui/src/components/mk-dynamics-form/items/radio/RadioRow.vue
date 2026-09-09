<script setup lang="ts">
import type { DynamicFormValue } from '../../type'
import { computed } from 'vue'
import type { FormField } from '@/components/mk-dynamics-form/type'
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
const emit = defineEmits<{ 'update:modelValue': [value: string | number | boolean | undefined] }>()

// 由原生单选组处理键盘操作、禁用状态及外层表单校验。
const selectedValue = computed({
  get: () => props.modelValue,
  set: (value: string | number | boolean | undefined) => emit('update:modelValue', value),
})

const textField = computed(() => {
  return props.formField.text_field ? props.formField.text_field : 'key'
})

const valueField = computed(() => {
  return props.formField.value_field ? props.formField.value_field : 'value'
})

const options = computed(() => {
  return props.formField.option_list ? props.formField.option_list : []
})
</script>

<template>
  <el-radio-group v-model="selectedValue">
    <el-radio-button v-for="option in options" :key="option[valueField]" :value="option[valueField]">
      {{ option[textField] }}
    </el-radio-button>
  </el-radio-group>
</template>
