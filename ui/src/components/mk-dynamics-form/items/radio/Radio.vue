<script setup lang="ts">
import type { MkDynamicFormValue } from '../../type'
import { computed } from 'vue'
import type { FormField } from '@/components/mk-dynamics-form/type'

defineOptions({ name: 'DynamicFormRadio' })

const props = defineProps<{
  formValue?: MkDynamicFormValue
  formfieldList?: Array<FormField>
  field: string
  otherParams: MkDynamicFormValue
  formField: FormField
  view?: boolean
}>()

const textField = computed(() => {
  return props.formField.text_field ? props.formField.text_field : 'key'
})

const valueField = computed(() => {
  return props.formField.value_field ? props.formField.value_field : 'value'
})

const option_list = computed(() => {
  return props.formField.option_list ? props.formField.option_list : []
})

const label = (option: MkDynamicFormValue) => {
  return option[textField.value]
}
</script>

<template>
  <el-radio-group v-bind="$attrs">
    <el-radio v-for="(item, index) in option_list" :key="index" :label="item[valueField]">
      <div v-html="label(item)"></div>
    </el-radio>
  </el-radio-group>
</template>
