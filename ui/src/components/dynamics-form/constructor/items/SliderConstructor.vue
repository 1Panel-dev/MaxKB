<template>
  <el-form-item label="取值范围" required>
    <el-col :span="11" style="padding-left: 0">
      <el-input-number style="width: 100%" v-model="formValue.min" controls-position="right" />
    </el-col>
    <el-col :span="2" class="text-center">
      <span class="text-gray-500">-</span>
    </el-col>
    <el-col :span="11">
      <el-input-number style="width: 100%" v-model="formValue.max" controls-position="right" />
    </el-col>
  </el-form-item>
  <el-form-item label="步长值" required>
    <el-input-number v-model="formValue.step" :min="0" controls-position="right" />
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

const rander = (form_data: any) => {
  const attrs = form_data.attrs
  formValue.value.option_list = form_data.option_list
  formValue.value.min = attrs.min
  formValue.value.max = attrs.max
  formValue.value.step = attrs.step
  formValue.value.default_value = form_data.default_value
}

defineExpose({ getData, rander })
onBeforeMount(() => {
  formValue.value.min = 0
  formValue.value.max = 20
  formValue.value.step = 0.1
  formValue.value.default_value = 1
})
</script>
<style lang="scss"></style>
