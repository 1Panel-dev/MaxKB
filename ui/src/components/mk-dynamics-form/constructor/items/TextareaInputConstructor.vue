<script setup lang="ts">
import type { DynamicFormValue } from '../../type'
import { computed, onMounted, watch } from 'vue'
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
watch(
  () => formValue.value.minlength,
  () => {
    if (formValue.value.minlength > formValue.value.maxlength) {
      formValue.value.maxlength = formValue.value.minlength
    }
  },
)
const getData = () => {
  return {
    input_type: 'TextareaInput',
    attrs: { maxlength: formValue.value.maxlength, minlength: formValue.value.minlength, 'show-word-limit': true, rows: 3 },
    default_value: formValue.value.default_value,
    show_default_value: formValue.value.show_default_value,
    props_info: {
      rules: formValue.value.required
        ? [
            { required: true, message: `请输入 ${formValue.value.label}` },
            {
              min: formValue.value.minlength,
              max: formValue.value.maxlength,
              message: `${formValue.value.label}长度在 ${formValue.value.minlength} 到 ${formValue.value.maxlength} 个字符`,
              trigger: 'blur',
            },
          ]
        : [
            {
              min: formValue.value.minlength,
              max: formValue.value.maxlength,
              message: `${formValue.value.label}长度在 ${formValue.value.minlength} 到 ${formValue.value.maxlength} 个字符`,
              trigger: 'blur',
            },
          ],
    },
  }
}
const render = (formData: DynamicFormValue) => {
  const attrs = formData.attrs || {}
  formValue.value.minlength = attrs.minlength
  formValue.value.maxlength = attrs.maxlength
  formValue.value.default_value = formData.default_value
  formValue.value.show_default_value = formData.show_default_value
}
const rules = computed(() => [
  {
    min: formValue.value.minlength,
    max: formValue.value.maxlength,
    message: `长度在 ${formValue.value.minlength} 到 ${formValue.value.maxlength} 个字符`,
    trigger: 'blur',
  },
])

defineExpose({ getData, render })
onMounted(() => {
  formValue.value.minlength = 0
  formValue.value.maxlength = 200
  formValue.value.default_value = ''
  if (formValue.value.show_default_value === undefined) {
    formValue.value.show_default_value = true
  }
})
</script>

<template>
  <el-form-item label="文本长度" required>
    <div class="flex w-full items-start gap-2">
      <el-form-item class="min-w-0 flex-1" :rules="[{ required: true, message: '请输入最小长度', trigger: 'change' }]" prop="minlength">
        <el-input-number v-model="formValue.minlength" class="w-full!" :min="1" :step="1" controls-position="right" align="left" step-strictly />
      </el-form-item>
      <span class="flex-center shrink-0">-</span>
      <el-form-item class="min-w-0 flex-1" :rules="[{ required: true, message: '请输入最大长度', trigger: 'change' }]" prop="maxlength">
        <el-input-number
          v-model="formValue.maxlength"
          class="w-full!"
          :min="formValue.minlength > formValue.maxlength ? formValue.minlength : 1"
          :step="1"
          controls-position="right"
          align="left"
          step-strictly
        />
      </el-form-item>
    </div>
  </el-form-item>

  <el-form-item
    class="mk-hide-asterisk"
    :required="formValue.required"
    prop="default_value"
    :rules="formValue.required ? [{ required: true, message: '请输入默认值' }, ...rules] : rules"
  >
    <template #label>
      <div class="flex-between">
        <span :class="formValue.required ? 'mk-required' : ''">默认值</span>
        <el-checkbox v-model="formValue.show_default_value" label="显示默认值" />
      </div>
    </template>
    <el-input
      v-model="formValue.default_value"
      :maxlength="formValue.maxlength"
      :minlength="formValue.minlength"
      placeholder="请输入默认值"
      show-word-limit
      :rows="3"
      type="textarea"
    />
  </el-form-item>
</template>
<style lang="scss" scoped></style>
