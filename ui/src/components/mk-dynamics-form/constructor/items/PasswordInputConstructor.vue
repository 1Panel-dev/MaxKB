<script setup lang="ts">
import type { DynamicFormValue } from '../../type'
import { computed, onMounted, watch } from 'vue'

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
    input_type: 'PasswordInput',
    attrs: {
      maxlength: formValue.value.maxlength,
      minlength: formValue.value.minlength,
      'show-word-limit': true,
      type: 'password',
      'show-password': true,
    },
    default_value: formValue.value.default_value,
    show_default_value: formValue.value.show_default_value,
    props_info: {
      rules: formValue.value.required
        ? [
            {
              required: true,
              message: `${formValue.value.label} 为必填属性`,
            },
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
  formValue.value.show_password = attrs['show-password']
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
  formValue.value.show_password = true

  if (formValue.value.show_default_value === undefined) {
    formValue.value.show_default_value = true
  }
})
</script>

<template>
  <el-form-item label="文本长度" required>
    <el-row class="w-full">
      <el-col :span="11">
        <el-form-item
          :rules="[
            {
              required: true,
              message: '最小长度必填',
              trigger: 'change',
            },
          ]"
          prop="minlength"
        >
          <el-input-number
            style="width: 100%"
            :min="1"
            :step="1"
            step-strictly
            v-model="formValue.minlength"
            controls-position="right"
          />
        </el-form-item>
      </el-col>
      <el-col :span="2" class="text-center">
        <span>-</span>
      </el-col>
      <el-col :span="11">
        <el-form-item
          :rules="[
            {
              required: true,
              message: '最大长度必填',
              trigger: 'change',
            },
          ]"
          prop="maxlength"
        >
          <el-input-number
            style="width: 100%"
            :min="formValue.minlength > formValue.maxlength ? formValue.minlength : 1"
            step-strictly
            :step="1"
            v-model="formValue.maxlength"
            controls-position="right"
          />
        </el-form-item>
      </el-col>
    </el-row>
  </el-form-item>

  <el-form-item
    class="defaultValueItem"
    :required="formValue.required"
    prop="default_value"
    label="默认值"
    :rules="
      formValue.required ? [{ required: true, message: '默认值为必填属性' }, ...rules] : rules
    "
  >
    <div class="defaultValueCheckbox">
      <el-checkbox v-model="formValue.show_default_value" label="显示默认值" />
    </div>

    <el-input
      v-model="formValue.default_value"
      :maxlength="formValue.maxlength"
      :minlength="formValue.minlength"
      placeholder="请输入默认值"
      show-word-limit
      type="password"
      show-password
    />
  </el-form-item>
</template>
<style lang="scss" scoped>
.defaultValueItem {
  position: relative;

  .defaultValueCheckbox {
    position: absolute;
    right: 0;
    top: -35px;
  }
}
</style>
