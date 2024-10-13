<template>
  <el-form-item label="最小长度" required>
    <el-input-number v-model="formValue.min_length" :min="0" controls-position="right" />
  </el-form-item>
  <el-form-item label="最大长度" required>
    <el-input-number v-model="formValue.max_length" :min="0" controls-position="right" />
  </el-form-item>
  <el-form-item
    label="默认值"
    :required="formValue.required"
    prop="default_value"
    :rules="formValue.required ? [{ required: true, message: '默认值 为必填属性' }] : []"
  >
    <el-input
      v-model="formValue.default_value"
      :maxlength="formValue.max_length"
      :minlength="formValue.min_length"
      placeholder="请输入默认值"
      show-word-limit
      type="text"
    />
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
    input_type: 'TextInput',
    attrs: {
      maxlength: formValue.value.max_length,
      minlength: formValue.value.min_length,
      'show-word-limit': true
    },
    default_value: formValue.value.default_value
  }
}
defineExpose({ getData })
onMounted(() => {
  formValue.value.min_length = 0
  formValue.value.max_length = 20
  formValue.value.default_value = ''
})
</script>
<style lang="scss"></style>
