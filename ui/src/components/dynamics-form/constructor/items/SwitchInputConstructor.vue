<template>
  <el-form-item
    label="默认值"
    :required="formValue.required"
    prop="default_value"
    :rules="formValue.required ? [{ required: true, message: '默认值 为必填属性' }] : []"
  >
    <el-switch v-model="formValue.default_value" />
  </el-form-item>
</template>
<script setup lang="ts">
import { computed, onMounted } from 'vue'

const props = defineProps<{
  modelValue: any
}>()
const emit = defineEmits(['update:modelValue'])
const formValue = computed({
  set: (item) => {
    emit('update:modelValue', item)
  },
  get: () => {
    return props.modelValue
  }
})

const getData = () => {
  return {
    input_type: 'SwitchInput',
    show_default_value: true,
    attrs: {},
    default_value: formValue.value.default_value
  }
}

const rander = (form_data: any) => {
  formValue.value.default_value = form_data.default_value || false
}
defineExpose({ getData, rander })
onMounted(() => {
  formValue.value.default_value = false
})
</script>
<style lang="scss"></style>
