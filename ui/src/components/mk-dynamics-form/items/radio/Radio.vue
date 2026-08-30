<script setup lang="ts">
import type { DynamicFormValue } from '../../type'
import { computed } from 'vue'
import type { FormField } from '@/components/mk-dynamics-form/type'

defineOptions({ name: 'DynamicFormRadio' })

const props = defineProps<{ formValue?: DynamicFormValue; formfieldList?: FormField[]; field: string; otherParams: DynamicFormValue; formField: FormField; view?: boolean }>()

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
  <el-radio-group v-bind="$attrs">
    <el-radio v-for="(item, index) in options" :key="index" :label="item[valueField]">
      <div v-html="label(item)"></div>
    </el-radio>
  </el-radio-group>
</template>
