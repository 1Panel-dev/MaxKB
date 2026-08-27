<script setup lang="ts">
import type { DynamicFormValue } from '../../type'
import type { FormField } from '@/components/mk-dynamics-form/type'
import SelectHeader from '@/components/mk-dynamics-form/items/common/SelectHeader.vue'
import { computed, useAttrs } from 'vue'
const attrs = useAttrs() as DynamicFormValue

const props = defineProps<{
  modelValue?: string
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
    return props.modelValue
  },
  set(value) {
    emit('update:modelValue', value)
    emit('change', props.formField)
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
  //置空
  if (props.modelValue && options.value && !attrs['allow-create']) {
    const oldItem = options.value.find((item) => item[valueField.value] === props.modelValue)
    if (!oldItem) {
      emit('update:modelValue', undefined)
    }
  }

  return option[textField.value]
}
</script>

<template>
  <el-select
    filterable
    :teleported="true"
    popper-class="dynamics-single-select"
    clearable
    v-bind="$attrs"
    v-model="_modelValue"
  >
    <template #header v-if="$attrs.popperHeader">
      <SelectHeader :header="$attrs.popperHeader" />
    </template>
    <el-option
      v-for="(item, index) in options"
      :key="index"
      teleported
      :label="label(item)"
      :value="item[valueField]"
    >
    </el-option>
  </el-select>
</template>
<style lang="scss">
.dynamics-single-select {
  .el-select-dropdown {
    max-width: 1px;
  }
}
</style>
