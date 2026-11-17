<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useI18n } from 'vue-i18n'
import type { DynamicFormValue } from '../../type'
import MkTagsEdit from '@/components/mk-tags-edit/index.vue'
const { t } = useI18n({ useScope: 'global' })

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
  formValue.value.limit = formData.attrs?.limit ?? 3
  formValue.value.max_file_size = formData.max_file_size ?? 10
  formValue.value.accept = formData.attrs?.accept ? formData.attrs.accept.split(',').map((item: string) => item.substring(1)) : ['jpg']
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
  <el-form-item
    :label="t('dynamicForm.fields.fileCount.label')"
    required
    prop="limit"
    :rules="[{ required: true, message: t('common.validation.inputRequired'), trigger: 'change' }]"
  >
    <el-input-number v-model="formValue.limit" :min="0" controls-position="right" align="left" />
  </el-form-item>
  <el-form-item
    :label="t('dynamicForm.fields.fileSize.label')"
    required
    prop="max_file_size"
    :rules="[{ required: true, message: t('common.validation.inputRequired'), trigger: 'change' }]"
  >
    <el-input-number v-model="formValue.max_file_size" :min="0" controls-position="right" align="left" />
  </el-form-item>
  <el-form-item
    :label="t('dynamicForm.fields.fileTypes.label')"
    required
    prop="accept"
    :rules="[{ required: true, message: t('dynamicForm.fields.fileTypes.requiredMessage'), trigger: 'change' }]"
  >
    <MkTagsEdit v-model="formValue.accept" />
  </el-form-item>
</template>
