<template>
  <div class="radio_content">
    <div
      v-for="item in option_list"
      :key="item.value"
      class="item"
      :class="[modelValue == item[valueField] ? 'active' : '']"
      @click="selected(item[valueField])"
    >
      {{ item[textField] }}
    </div>
  </div>
</template>
<script lang="ts" setup>
import { watch, computed } from 'vue'
import type { FormField } from '@/components/dynamics-form/type'
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

const selected = (activeValue: string | number) => {
  emit('update:modelValue', activeValue)
}
const emit = defineEmits(['update:modelValue'])

const textField = computed(() => {
  return props.formField.text_field ? props.formField.text_field : 'key'
})

const valueField = computed(() => {
  return props.formField.value_field ? props.formField.value_field : 'value'
})

const option_list = computed(() => {
  return props.formField.option_list ? props.formField.option_list : []
})
watch(
  option_list,
  () => {
    if (
      (option_list.value &&
        option_list.value.length > 0 &&
        !option_list.value.some((item) => item.value === props.modelValue)) ||
      !props.modelValue
    ) {
      emit('update:modelValue', option_list.value[0][valueField.value])
    }
  },
  { immediate: true }
)
</script>
<style lang="scss" scoped>
.radio_content {
  height: 32px;
  display: inline-flex;
  border: 1px solid #bbbfc4;
  border-radius: 4px;
  font-weight: 400;
  font-size: 14px;
  color: #1f2329;
  padding: 3px 4px;
  box-sizing: border-box;

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
