<script setup lang="ts">
import { computed, inject } from 'vue'
import DOMPurify from 'dompurify'
import { formItemContextKey, useFormDisabled } from 'element-plus'
import type { DynamicFormValue } from '../../type'
import type { FormField } from '@/components/mk-dynamics-form/type'

const inputDisabled = useFormDisabled()

const props = defineProps<{
  formValue?: DynamicFormValue
  formfieldList?: FormField[]
  field: string
  otherParams: DynamicFormValue
  formField: FormField
  view?: boolean
  // 选中的值
  modelValue?: DynamicFormValue
  disabled?: boolean
}>()
const elFormItem = inject(formItemContextKey, void 0)
const emit = defineEmits<{ change: [value: DynamicFormValue]; 'update:modelValue': [value: DynamicFormValue] }>()

const isOptionActive = (optionValue: DynamicFormValue) => {
  if (props.modelValue === optionValue) return true

  return props.modelValue !== undefined && props.modelValue !== null && optionValue !== undefined && optionValue !== null && String(props.modelValue) === String(optionValue)
}

const selectOption = (activeValue: string | number) => {
  if (inputDisabled.value) return

  emit('update:modelValue', activeValue)
  emit('change', activeValue)
  if (elFormItem?.validate) {
    elFormItem.validate('change')
  }
}

const textField = computed(() => {
  return props.formField.text_field ? props.formField.text_field : 'key'
})

const valueField = computed(() => {
  return props.formField.value_field ? props.formField.value_field : 'value'
})

const options = computed(() => {
  return props.formField.option_list ? props.formField.option_list : []
})

// 选项文本允许 HTML，渲染前经 DOMPurify 净化，避免存储型 XSS。
const optionLabel = (option: DynamicFormValue) => {
  return DOMPurify.sanitize(String(option[textField.value] ?? '')) || '\u200D'
}
</script>

<template>
  <div class="grid w-full grid-cols-1 gap-2 lg:grid-cols-2">
    <div
      v-for="(item, index) in options"
      :key="item[valueField] ?? index"
      class="cursor-pointer break-all rounded-md border px-4 py-2 text-center"
      :class="[inputDisabled ? 'cursor-not-allowed! bg-N100! text-N600!' : '', isOptionActive(item[valueField]) ? 'border-primary! text-primary!' : '']"
      @click="selectOption(item[valueField])"
    >
      <!-- eslint-disable-next-line vue/no-v-html -- 内容已经 DOMPurify 净化 -->
      <span v-html="optionLabel(item)"></span>
    </div>
  </div>
</template>
