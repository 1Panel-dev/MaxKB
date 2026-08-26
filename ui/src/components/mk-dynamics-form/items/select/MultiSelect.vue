<script setup lang="ts">
import type { MkDynamicFormValue } from '../../type'
import type { FormField } from '@/components/mk-dynamics-form/type'
import SelectHeader from '@/components/mk-dynamics-form/items/common/SelectHeader.vue'
import { computed } from 'vue'

const props = defineProps<{
  modelValue?: Array<MkDynamicFormValue>
  formValue?: MkDynamicFormValue
  formfieldList?: Array<FormField>
  field: string
  otherParams: MkDynamicFormValue
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

const option_list = computed(() => {
  return props.formField.option_list ? props.formField.option_list : []
})

const label = (option: MkDynamicFormValue) => {
  return option[textField.value]
}
</script>

<template>
  <el-select
    class="m-2"
    multiple
    filterable
    allow-create
    clearable
    default-first-option
    :reserve-keyword="false"
    v-bind="$attrs"
    v-model="_modelValue"
  >
    <template #header v-if="$attrs.popperHeader">
      <SelectHeader :header="$attrs.popperHeader" />
    </template>
    <el-option
      v-for="(item, index) in option_list"
      :key="index"
      :label="label(item)"
      :value="item[valueField]"
    >
    </el-option>
  </el-select>
</template>
