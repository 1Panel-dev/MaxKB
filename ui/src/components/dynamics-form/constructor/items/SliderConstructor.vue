<template>
  <el-form-item label="最小值" required>
    <el-input-number v-model="formValue.min" :min="0" controls-position="right" />
  </el-form-item>
  <el-form-item label="最大值" required>
    <el-input-number v-model="formValue.max" :min="0" controls-position="right" />
  </el-form-item>
  <el-form-item label="步长值" required>
    <el-input-number v-model="formValue.step" :min="0" controls-position="right" />
  </el-form-item>
  <el-form-item label="精确值" required>
    <el-input-number v-model="formValue.precision" :min="0" controls-position="right" />
  </el-form-item>
  <el-form-item
    label="默认值"
    :required="formValue.required"
    prop="default_value"
    :rules="formValue.required ? [{ required: true, message: '默认值 为必填属性' }] : []"
  >
    <el-slider
      v-model="formValue.default_value"
      show-input
      :show-input-controls="false"
      :max="formValue.max"
      :min="formValue.min"
      :step="formValue.step"
      :precision="formValue.precision"
    />
  </el-form-item>
</template>
<script setup lang="ts">
import { computed, onBeforeMount } from 'vue'

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
    input_type: 'Slider',
    attrs: {
      min: formValue.value.min,
      max: formValue.value.max,
      step: formValue.value.step,
      precision: formValue.value.precision,
      'show-input-controls': false,
      'show-input': true
    },
    default_value: formValue.value.default_value
  }
}
defineExpose({ getData })
onBeforeMount(() => {
  formValue.value.min = props.modelValue.attrs?.min || 0
  formValue.value.max = props.modelValue.attrs?.max || 20
  formValue.value.step = props.modelValue.attrs?.step || 0.1
  formValue.value.precision = props.modelValue.attrs?.precision || 1
  formValue.value.default_value = props.modelValue.default_value || 1
})
</script>
<style lang="scss"></style>
