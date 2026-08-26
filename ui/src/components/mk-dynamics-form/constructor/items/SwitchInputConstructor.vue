<script setup lang="ts">
import type { MkDynamicFormValue } from '../../type'
import { computed, onMounted } from 'vue'

const props = defineProps<{
  modelValue: MkDynamicFormValue
}>()
const emit = defineEmits(['update:modelValue'])
const formValue = computed({
  set: (item) => {
    emit('update:modelValue', item)
  },
  get: () => {
    return props.modelValue
  },
})

const getData = () => {
  return {
    input_type: 'SwitchInput',
    show_default_value: true,
    attrs: {},
    default_value: formValue.value.default_value,
  }
}

const render = (form_data: MkDynamicFormValue) => {
  formValue.value.default_value = form_data.default_value || false
}
defineExpose({ getData, render })
onMounted(() => {
  formValue.value.default_value = false
})
</script>

<template>
  <el-form-item
    label="默认值"
    :required="formValue.required"
    prop="default_value"
    :rules="
      formValue.required
        ? [
            {
              required: true,
              message: '默认值为必填属性',
            },
          ]
        : []
    "
    @click.prevent
  >
    <el-switch v-model="formValue.default_value" />
  </el-form-item>
</template>
