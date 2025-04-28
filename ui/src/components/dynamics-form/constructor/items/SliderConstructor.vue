<template>
  <el-form-item :label="$t('dynamicsForm.Slider.showInput.label')" required prop="showInput">
    <el-switch v-model="formValue.showInput" />
  </el-form-item>
  <el-form-item :label="$t('dynamicsForm.Slider.valueRange.label')" required>
    <el-col :span="11" style="padding-left: 0">
      <el-form-item
        :rules="[
          {
            required: true,
            message: $t('dynamicsForm.Slider.valueRange.minRequired'),
            trigger: 'change'
          }
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
            message: $t('dynamicsForm.Slider.valueRange.maxRequired'),
            trigger: 'change'
          }
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
    <el-form-item
      :label="$t('dynamicsForm.Slider.step.label')"
      required
      prop="step"
      :rules="step_rules"
    >
      <el-input-number
        style="width: 100%"
        v-model="formValue.step"
        :min="0"
        controls-position="right"
      />
    </el-form-item>
  </el-col>

  <el-form-item
    :label="$t('dynamicsForm.default.label')"
    :required="formValue.required"
    prop="default_value"
    :rules="
      formValue.required
        ? [{ required: true, message: $t('dynamicsForm.default.requiredMessage') }]
        : []
    "
  >
    <el-slider
      v-model="formValue.default_value"
      :show-input="formValue.showInput"
      :show-input-controls="false"
      :max="formValue.max"
      :min="formValue.min"
      :step="formValue.step == 0 ? 0.1 : formValue.step"
      :precision="formValue.precision"
    />
  </el-form-item>
</template>
<script setup lang="ts">
import { computed, onBeforeMount, watch } from 'vue'
import { t } from '@/locales'
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
      'show-input': formValue.value.showInput
    },
    props_info: {
      rules: [
        {
          message: formValue.value.label + ' ' + t('dynamicsForm.tip.requiredMessage'),
          trigger: 'blur',
          required: formValue.value.required
        }
      ]
    },
    show_default_value: true,
    default_value: formValue.value.default_value
  }
}
watch(
  () => formValue.value.min,
  () => {
    if (formValue.value.min > formValue.value.max) {
      formValue.value.max = formValue.value.min
    }
  }
)
const rander = (form_data: any) => {
  const attrs = form_data.attrs
  formValue.value.option_list = form_data.option_list
  formValue.value.min = attrs.min
  formValue.value.max = attrs.max
  formValue.value.step = attrs.step
  formValue.value.showInput = attrs['show-input']
  formValue.value.default_value = form_data.default_value
}
const step_rules = [
  {
    required: true,
    validator: (rule: any, value: any, callback: any) => {
      if (!value) {
        callback(new Error(t('dynamicsForm.Slider.step.requiredMessage1')))
        return false
      }
      if (value === 0) {
        callback(new Error(t('dynamicsForm.Slider.step.requiredMessage2')))
        return false
      }
      return true
    },
    trigger: 'blur'
  }
]
defineExpose({ getData, rander })
onBeforeMount(() => {
  formValue.value.min = 0
  formValue.value.max = 20
  formValue.value.step = 0.1
  formValue.value.default_value = 1
  formValue.value.showInput = true
})
</script>
<style lang="scss"></style>
