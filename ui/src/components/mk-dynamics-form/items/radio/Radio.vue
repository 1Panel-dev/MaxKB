<script setup lang="ts">
import { computed } from 'vue'
import DOMPurify from 'dompurify'
import type { DynamicFormValue } from '../../type'
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

// 选项文本允许 HTML，渲染前经 DOMPurify 净化，避免存储型 XSS。
const label = (option: DynamicFormValue) => {
  return DOMPurify.sanitize(String(option[textField.value] ?? ''))
}
</script>

<template>
  <el-radio-group v-bind="$attrs">
    <el-radio v-for="(item, index) in options" :key="index" :label="item[valueField]">
      <!-- eslint-disable-next-line vue/no-v-html -- 内容已经 DOMPurify 净化 -->
      <div v-html="label(item)"></div>
    </el-radio>
  </el-radio-group>
</template>
