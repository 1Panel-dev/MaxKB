<script setup lang="ts">
import type { DynamicFormValue } from '../../type'
import { computed, ref } from 'vue'
import type { FormField } from '@/components/mk-dynamics-form/type'
import DynamicsForm from '@/components/mk-dynamics-form/index.vue'
const emit = defineEmits(['update:modelValue', 'change'])

const props = defineProps<{
  modelValue?: DynamicFormValue
  formValue?: DynamicFormValue
  formfieldList?: FormField[]
  otherParams: DynamicFormValue
  formField: FormField
  view?: boolean
}>()

const data = computed({
  get: () => {
    if (props.modelValue) {
      return props.modelValue
    }
    return {}
  },
  set: ($event) => {
    emit('update:modelValue', $event)
  },
})

const other = computed(() => {
  return { ...(props.formfieldList ? props.formfieldList : {}), ...props.otherParams }
})
// 校验实例对象
const dynamicsFormRef = ref<InstanceType<typeof DynamicsForm>>()
/**
 * 组件样式
 */
const formStyle = computed(() => {
  return fieldProps.value.form_style ? fieldProps.value.form_style : {}
})
const fieldProps = computed(() => {
  return props.formField.props_info ? props.formField.props_info : {}
})

const style = computed(() => {
  return fieldProps.value.style ? fieldProps.value.style : {}
})
/**
 * 校验方法
 */
function validate() {
  if (dynamicsFormRef.value) {
    return dynamicsFormRef.value.validate()
  }
  return Promise.resolve()
}
defineExpose({ validate })
</script>

<template>
  <el-card :style="style">
    <DynamicsForm
      :read-only="view"
      :style="formStyle"
      ref="dynamicsFormRef"
      v-model="data"
      :other-params="other"
      :render-data="formField.children ? formField.children : []"
      v-bind="$attrs"
      :parent-field="formField.field"
      label-position="top"
      require-asterisk-position="right"
    ></DynamicsForm>
  </el-card>
</template>
