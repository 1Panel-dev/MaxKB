<template>
  <el-form-item :label="$t('dynamicsForm.TextInput.length.label')" required>
    <el-row class="w-full">
      <el-col :span="11">
        <el-form-item
          :rules="[
            {
              required: true,
              message: $t('dynamicsForm.TextInput.length.minRequired'),
              trigger: 'change'
            }
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
              message: $t('dynamicsForm.TextInput.length.maxRequired'),
              trigger: 'change'
            }
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
        /></el-form-item>
      </el-col>
    </el-row>
  </el-form-item>

  <el-form-item
    class="defaultValueItem"
    :required="formValue.required"
    prop="default_value"
    :label="$t('dynamicsForm.default.label')"
    :rules="
      formValue.required ? [{ required: true, message: `${$t('dynamicsForm.default.label')}${$t('dynamicsForm.default.requiredMessage')}` }, ...rules] : rules
    "
  >
    <div class="defaultValueCheckbox">
      <el-checkbox
        v-model="formValue.show_default_value"
        :label="$t('dynamicsForm.default.show')"
      />
    </div>

    <el-input
      v-model="formValue.default_value"
      :maxlength="formValue.maxlength"
      :minlength="formValue.minlength"
      :placeholder="$t('dynamicsForm.default.placeholder')"
      show-word-limit
      type="text"
    />
  </el-form-item>
</template>
<script setup lang="ts">
import { computed, onMounted, watch } from 'vue'
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
watch(
  () => formValue.value.minlength,
  () => {
    if (formValue.value.minlength > formValue.value.maxlength) {
      formValue.value.maxlength = formValue.value.minlength
    }
  }
)
const getData = () => {
  return {
    input_type: 'TextInput',
    attrs: {
      maxlength: formValue.value.maxlength,
      minlength: formValue.value.minlength,
      'show-word-limit': true
    },
    default_value: formValue.value.default_value,
    show_default_value: formValue.value.show_default_value,
    props_info: {
      rules: formValue.value.required
        ? [
            { required: true, message: `${formValue.value.label} ${t('dynamicsForm.default.requiredMessage')}` },
            {
              min: formValue.value.minlength,
              max: formValue.value.maxlength,
              message: `${formValue.value.label}${t('dynamicsForm.TextInput.length.requiredMessage1')} ${formValue.value.minlength} ${t('dynamicsForm.TextInput.length.requiredMessage2')} ${formValue.value.maxlength} ${t('dynamicsForm.TextInput.length.requiredMessage3')}`,
              trigger: 'blur'
            }
          ]
        : [
            {
              min: formValue.value.minlength,
              max: formValue.value.maxlength,
              message: `${formValue.value.label}${t('dynamicsForm.TextInput.length.requiredMessage1')} ${formValue.value.minlength} ${t('dynamicsForm.TextInput.length.requiredMessage2')} ${formValue.value.maxlength} ${t('dynamicsForm.TextInput.length.requiredMessage3')}`,
              trigger: 'blur'
            }
          ]
    }
  }
}
const rander = (form_data: any) => {
  const attrs = form_data.attrs || {}
  formValue.value.minlength = attrs.minlength
  formValue.value.maxlength = attrs.maxlength
  formValue.value.default_value = form_data.default_value
  formValue.value.show_default_value = form_data.show_default_value
}
const rangeRules = [
  {
    required: true,
    validator: (rule: any, value: any, callback: any) => {
      if (!formValue.value.minlength) {
        callback(new Error(t('dynamicsForm.TextInput.length.requiredMessage4')))
      }
      if (!formValue.value.maxlength) {
        callback(new Error(t('dynamicsForm.TextInput.length.requiredMessage4')))
      }
      return true
    },
    message: `${formValue.value.label} ${t('dynamicsForm.default.requiredMessage')}`
  }
]
const rules = computed(() => [
  {
    min: formValue.value.minlength,
    max: formValue.value.maxlength,
    message: `${t('dynamicsForm.TextInput.length.requiredMessage1')} ${formValue.value.minlength} ${t('dynamicsForm.TextInput.length.requiredMessage2')} ${formValue.value.maxlength} ${t('dynamicsForm.TextInput.length.requiredMessage3')}`,
    trigger: 'blur'
  }
])

defineExpose({ getData, rander })
onMounted(() => {
  formValue.value.minlength = 0
  formValue.value.maxlength = 200
  formValue.value.default_value = ''
  // console.log(formValue.value.show_default_value)
  if (formValue.value.show_default_value === undefined) {
    formValue.value.show_default_value = true
  }
})
</script>
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
