<script setup lang="ts">
import type { DynamicFormValue } from '../../type'
import { computed, onMounted } from 'vue'

const props = defineProps<{
  modelValue: DynamicFormValue
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

const render = (formData: DynamicFormValue) => {
  formValue.value.default_value = formData.default_value || false
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
              message: '请选择默认值',
            },
          ]
        : []
    "
    @click.prevent
  >
    <el-switch v-model="formValue.default_value" />
  </el-form-item>
</template>
