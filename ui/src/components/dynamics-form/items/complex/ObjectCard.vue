<template>
  <el-card :style="style">
    <DynamicsForm
      :read-only="view"
      :style="formStyle"
      label-position="top"
      require-asterisk-position="right"
      ref="dynamicsFormRef"
      v-model="data"
      :other-params="other"
      :render_data="formField.children ? formField.children : []"
      v-bind="$attrs"
      :parent_field="formField.field"
    ></DynamicsForm>
  </el-card>
</template>
<script setup lang="ts">
import { computed, ref } from 'vue'
import type { FormField } from '@/components/dynamics-form/type'
import DynamicsForm from '@/components/dynamics-form/index.vue'
const emit = defineEmits(['update:modelValue', 'change'])

const props = defineProps<{
  modelValue?: any
  formValue?: any
  formfieldList?: Array<FormField>
  otherParams: any
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
  }
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
  return props_info.value.form_style ? props_info.value.form_style : {}
})
const props_info = computed(() => {
  return props.formField.props_info ? props.formField.props_info : {}
})

const style = computed(() => {
  return props_info.value.style ? props_info.value.style : {}
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
defineExpose({
  validate
})
</script>
<style lang="scss" scoped></style>
