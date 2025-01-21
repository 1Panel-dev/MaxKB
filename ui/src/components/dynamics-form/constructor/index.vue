<template>
  <el-form
    @submit.prevent
    ref="ruleFormRef"
    class="mb-24"
    label-width="auto"
    :model="form_data"
    v-bind="$attrs"
  >
    <el-form-item :label="$t('dynamicsForm.paramForm.field.label')" :required="true" prop="field" :rules="rules.field">
      <el-input
        v-model="form_data.field"
        :maxlength="64"
        :placeholder="$t('dynamicsForm.paramForm.field.placeholder')"
        show-word-limit
      />
    </el-form-item>
    <el-form-item :label="$t('dynamicsForm.paramForm.name.label')" :required="true" prop="label" :rules="rules.label">
      <el-input
        v-model="form_data.label"
        :maxlength="64"
        show-word-limit
        :placeholder="$t('dynamicsForm.paramForm.name.placeholder')"
      />
    </el-form-item>
    <el-form-item :label="$t('dynamicsForm.paramForm.tooltip.label')">
      <el-input
        v-model="form_data.tooltip"
        :maxlength="128"
        show-word-limit
        :placeholder="$t('dynamicsForm.paramForm.tooltip.placeholder')"
      />
    </el-form-item>
    <el-form-item :label="$t('dynamicsForm.paramForm.required.label')" :required="true" prop="required" :rules="rules.required">
      <el-switch v-model="form_data.required" :active-value="true" :inactive-value="false" />
    </el-form-item>
    <el-form-item :label="$t('dynamicsForm.paramForm.input_type.label')" :required="true" prop="input_type" :rules="rules.input_type">
      <el-select v-model="form_data.input_type" :placeholder="$t('dynamicsForm.paramForm.input_type.placeholder')">
        <el-option
          v-for="input_type in input_type_list"
          :key="input_type.value"
          :label="input_type.label"
          :value="input_type.value"
        />
      </el-select>
    </el-form-item>
    <component
      v-if="form_data.input_type"
      ref="componentFormRef"
      v-model="form_data"
      :is="form_data.input_type"
    ></component>
  </el-form>
</template>
<script setup lang="ts">
import { onMounted, ref, nextTick } from 'vue'
import type { FormInstance } from 'element-plus'
import _ from 'lodash'
import { input_type_list as input_type_list_data } from '@/components/dynamics-form/constructor/data'
import { t } from '@/locales'
const props = withDefaults(
  defineProps<{
    modelValue?: any
    input_type_list?: Array<{ label: string; value: string }>
  }>(),
  {
    input_type_list: () =>
      input_type_list_data.map((item) => ({ label: item.label, value: item.value + 'Constructor' }))
  }
)
const emit = defineEmits(['update:modelValue'])

const ruleFormRef = ref<FormInstance>()

const componentFormRef = ref<any>()
const form_data = ref<any>({
  label: '',
  field: '',
  tooltip: '',
  required: false,
  input_type: ''
})
const rules = {
  label: [{ required: true, message: t('dynamicsForm.paramForm.name.requiredMessage') }],
  field: [{ required: true, message: t('dynamicsForm.paramForm.field.requiredMessage') }],
  required: [{ required: true, message: t('dynamicsForm.paramForm.required.requiredMessage') }],
  input_type: [{ required: true, message: t('dynamicsForm.paramForm.input_type.requiredMessage') }]
}
const getData = () => {
  let label: string | any = form_data.value.label
  if (form_data.value.tooltip) {
    label = {
      input_type: 'TooltipLabel',
      label: form_data.value.label,
      attrs: { tooltip: form_data.value.tooltip },
      props_info: {}
    }
  }
  return {
    label: label,
    required: form_data.value.required,
    field: form_data.value.field,
    default_value: form_data.value.default_value,
    show_default_value: form_data.value.show_default_value,
    ...componentFormRef.value.getData()
  }
}

const validate = () => {
  if (ruleFormRef.value) {
    return ruleFormRef.value?.validate()
  }
  return Promise.resolve()
}

onMounted(() => {
  if (props.modelValue) {
    rander(props.modelValue)
  }
})
const rander = (data: any) => {
  form_data.value.required = data.required ? data.required : false
  form_data.value.field = data.field
  if (data.show_default_value !== undefined) {
    form_data.value.show_default_value = data.show_default_value
  }
  if (data.input_type) {
    form_data.value.input_type = data.input_type + 'Constructor'
  }

  if (data.label && data.label.input_type === 'TooltipLabel') {
    form_data.value.tooltip = data.label.attrs.tooltip
    form_data.value.label = data.label.label
  } else {
    form_data.value.label = data.label
  }
  nextTick(() => {
    componentFormRef.value?.rander(data)
  })
}

defineExpose({ getData, validate, rander })
</script>
<style lang="scss"></style>
