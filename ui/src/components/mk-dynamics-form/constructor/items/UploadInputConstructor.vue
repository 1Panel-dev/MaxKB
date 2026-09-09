<script setup lang="ts">
import type { DynamicFormValue } from '../../type'
import { computed, onMounted } from 'vue'
import MkTagsEdit from '@/components/mk-tags-edit/index.vue'
const props = defineProps<{ modelValue: DynamicFormValue }>()

const emit = defineEmits(['update:modelValue'])
const formValue = computed({
  set: (item) => {
    emit('update:modelValue', item)
  },
  get: () => {
    return props.modelValue
  },
})

const render = (formData: DynamicFormValue) => {
  formValue.value.default_value = []
  formValue.value.limit = formData.attrs.limit || 3
  formValue.value.max_file_size = formData.max_file_size || 10
  formValue.value.accept = formData.attrs.accept ? formData.attrs.accept.split(',').map((item: string) => item.substring(1)) : ['jpg']
}
const getData = () => {
  return {
    input_type: 'UploadInput',
    attrs: { accept: formValue.value.accept.map((item: DynamicFormValue) => '.' + item).join(','), limit: formValue.value.limit },
    max_file_size: formValue.value.max_file_size,
    default_value: [],
    show_default_value: formValue.value.show_default_value,
  }
}
defineExpose({ getData, render })

onMounted(() => {
  formValue.value.default_value = []
  formValue.value.limit = 3
  formValue.value.max_file_size = 10
  formValue.value.accept = ['jpg']
  if (formValue.value.show_default_value === undefined) {
    formValue.value.show_default_value = true
  }
})
</script>

<template>
  <!-- // TODO 待设计 -->
  <el-form-item label="单次上传最多文件数" required prop="limit">
    <el-input-number
      style="width: 100%"
      v-model="formValue.limit"
      :rules="[{ required: true, message: '单次上传最多文件数必填', trigger: 'change' }]"
      :min="0"
      controls-position="right"
      align="left"
    />
  </el-form-item>
  <el-form-item
    label="每个文件最大(MB)"
    required
    prop="max_file_size"
    :rules="[{ required: true, message: '每个文件最大(MB)必填', trigger: 'change' }]"
  >
    <el-input-number style="width: 100%" v-model="formValue.max_file_size" :min="0" controls-position="right" align="left" />
  </el-form-item>
  <el-form-item label="文件类型" required prop="accept" :rules="[{ required: true, message: '文件类型必填', trigger: 'change' }]">
    <MkTagsEdit v-model="formValue.accept" />
  </el-form-item>
</template>
