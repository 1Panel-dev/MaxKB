<script setup lang="ts">
import type { DynamicFormValidatorCallback, DynamicFormValue } from '../../type'
import { computed, onBeforeMount, watch } from 'vue'
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
    input_type: 'Slider',
    attrs: {
      min: formValue.value.min,
      max: formValue.value.max,
      step: formValue.value.step,
      precision: formValue.value.precision,
      'show-input-controls': false,
      'show-input': formValue.value.showInput,
    },
    props_info: {
      rules: [
        {
          message: `请输入 ${formValue.value.label}`,
          trigger: 'blur',
          required: formValue.value.required,
        },
      ],
    },
    show_default_value: true,
    default_value: formValue.value.default_value,
  }
}
watch(
  () => formValue.value.min,
  () => {
    if (formValue.value.min > formValue.value.max) {
      formValue.value.max = formValue.value.min
    }
  },
)
const render = (formData: DynamicFormValue) => {
  const attrs = formData.attrs
  formValue.value.option_list = formData.option_list
  formValue.value.min = attrs.min
  formValue.value.max = attrs.max
  formValue.value.step = attrs.step
  formValue.value.showInput = attrs['show-input']
  formValue.value.default_value = formData.default_value
}
const stepRules = [
  {
    required: true,
    validator: (
      _rule: unknown,
      value: DynamicFormValue,
      callback: DynamicFormValidatorCallback,
    ) => {
      if (value === 0) {
        callback(new Error('步长不能为 0'))
        return false
      }
      if (!value) {
        callback(new Error('请输入步长值'))
        return false
      }

      return true
    },
    trigger: 'blur',
  },
]
defineExpose({ getData, render })
onBeforeMount(() => {
  formValue.value.min = 0
  formValue.value.max = 20
  formValue.value.step = 0.1
  formValue.value.default_value = 1
  formValue.value.showInput = true
})
</script>

<template>
  <el-form-item label="是否带输入框" required prop="showInput" @click.prevent>
    <el-switch v-model="formValue.showInput" />
  </el-form-item>
  <!-- // TODO 待调整 -->
  <el-form-item label="取值范围" required>
    <el-col :span="11" style="padding-left: 0">
      <el-form-item
        :rules="[
          {
            required: true,
            message: '最小值必填',
            trigger: 'change',
          },
        ]"
        prop="min"
      >
        <el-input-number style="width: 100%" v-model="formValue.min" controls-position="right"
      /></el-form-item>
    </el-col>
    <el-col :span="2" class="text-center">
      <span class="text-gray-500">-</span>
    </el-col>
    <el-col :span="11">
      <el-form-item
        :rules="[
          {
            required: true,
            message: '最大值必填',
            trigger: 'change',
          },
        ]"
        prop="max"
        ><el-input-number
          prop="max"
          style="width: 100%"
          v-model="formValue.max"
          :min="formValue.min > formValue.max ? formValue.min : undefined"
          controls-position="right"
      /></el-form-item>
    </el-col>
  </el-form-item>
  <el-col :span="11" style="padding-left: 0">
    <el-form-item label="步长值" required prop="step" :rules="stepRules">
      <el-input-number
        style="width: 100%"
        v-model="formValue.step"
        :min="0"
        controls-position="right"
      />
    </el-form-item>
  </el-col>

  <el-form-item
    label="默认值"
    :required="formValue.required"
    prop="default_value"
    :rules="formValue.required ? [{ required: true, message: '为必填属性' }] : []"
  >
    <el-slider
      v-model="formValue.default_value"
      :show-input="formValue.showInput"
      :show-input-controls="false"
      :max="formValue.max"
      :min="formValue.min"
      :step="formValue.step === 0 ? 0.1 : formValue.step"
      :precision="formValue.precision"
    />
  </el-form-item>
</template>
