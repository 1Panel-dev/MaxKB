<script setup lang="ts">
import type { DynamicFormValue } from '../../type'
import type { FormField } from '@/components/mk-dynamics-form/type'
import { computed } from 'vue'

const props = defineProps<{
  modelValue?: DynamicFormValue[]
  formValue?: DynamicFormValue
  formfieldList?: FormField[]
  field: string
  otherParams: DynamicFormValue
  formField: FormField
  view?: boolean
}>()

const emit = defineEmits(['update:modelValue', 'change'])

const _modelValue = computed({
  get() {
    if (props.modelValue) {
      return props.modelValue
    }
    return []
  },
  set($event) {
    emit('update:modelValue', $event)
  },
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

const label = (option: DynamicFormValue) => {
  return option[textField.value]
}
</script>

<template>
  <el-select
    multiple
    filterable
    allow-create
    clearable
    default-first-option
    :reserve-keyword="false"
    v-bind="$attrs"
    v-model="_modelValue"
  >
    <el-option
      v-for="(item, index) in options"
      :key="index"
      :label="label(item)"
      :value="item[valueField]"
    >
    </el-option>
  </el-select>
</template>
