<template>
  <div class="multi_row">
    <div
      v-for="item in option_list"
      :key="item.value"
      class="item"
      :class="[
        inputDisabled ? 'is-disabled' : '',
        _value.includes(item[valueField]) ? 'active' : '',
      ]"
      @click="selected(item[valueField])"
    >
      {{ item[textField] }}
    </div>
  </div>
</template>
<script lang="ts" setup>
import { computed, inject } from 'vue'
import type { FormField } from '@/components/dynamics-form/type'
import { useFormDisabled, formItemContextKey } from 'element-plus'
const inputDisabled = useFormDisabled()
const props = defineProps<{
  formValue?: any
  formfieldList?: Array<FormField>
  field: string
  otherParams: any
  formField: FormField
  view?: boolean
  // 选中的值
  modelValue?: any
}>()
const elFormItem = inject(formItemContextKey, void 0)
const selected = (activeValue: string | number) => {
  if (_value.value.includes(activeValue)) {
    emit(
      'update:modelValue',
      props.modelValue.filter((i: any) => i != activeValue),
    )
  } else {
    emit('update:modelValue', reset(activeValue))
  }
  if (elFormItem?.validate) {
    elFormItem.validate('change')
  }
}
const reset = (activeValue: string | number) => {
  const _result = props.modelValue ? [...props.modelValue, activeValue] : [activeValue]
  return _result.filter((r) => option_value_list.value.includes(r))
}

const _value = computed(() => {
  return props.modelValue ? props.modelValue : []
})
const emit = defineEmits(['update:modelValue'])

const textField = computed(() => {
  return props.formField.text_field ? props.formField.text_field : 'key'
})

const valueField = computed(() => {
  return props.formField.value_field ? props.formField.value_field : 'value'
})
const option_value_list = computed(() => {
  return option_list.value.map((item) => item[valueField.value])
})
const option_list = computed(() => {
  return props.formField.option_list ? props.formField.option_list : []
})
</script>
<style lang="scss" scoped>
.multi_row {
  // height: 32px;
  display: inline-flex;
  border: 1px solid #bbbfc4;
  border-radius: 4px;
  font-weight: 400;
  font-size: 14px;
  color: var(--el-text-color-primary);
  padding: 3px 4px;
  box-sizing: border-box;
  white-space: nowrap;
  .is-disabled {
    border: 1px solid var(--el-card-border-color);
    background-color: var(--el-fill-color-light);
    color: var(--el-text-color-placeholder);
    cursor: not-allowed;
    &:hover {
      cursor: not-allowed;
    }
  }
  .active {
    border-radius: 4px;
    background: var(--el-color-primary-light-9);
    color: var(--el-color-primary);
  }
  .item {
    cursor: pointer;
    margin: 0px 2px;
    padding: 2px 8px;
    height: 20px;
    display: flex;
    justify-content: center;
    align-items: center;
    &:last-child {
      margin: 0 4px 0 2px;
    }
    &:first-child {
      margin: 0 2px 0 4px;
    }
  }
}
</style>
