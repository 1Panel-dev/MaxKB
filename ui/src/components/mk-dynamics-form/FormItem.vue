<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import type { DynamicFormValue, FormField, FormFieldLabel, SerializedFormRule } from './type'
import type { Dict } from '@/api/types'
import type { FormItemRule } from 'element-plus'
import type { Component } from 'vue'
import { getUploadValidationMessage } from '@/components/mk-drag-upload/validation'
import FormItemLabel from './FormItemLabel.vue'
import { isSelectionFieldType } from './constant'
import { sanitizeFieldAttrs } from './safe-attrs'

defineOptions({ name: 'MkDynamicsFormItem' })
const { t } = useI18n({ useScope: 'global' })

interface DynamicFieldComponent {
  validate?: () => Promise<unknown>
  validateRules?: (rule: unknown, value: DynamicFormValue, callback: (error?: Error) => void) => void
}

const itemModules = import.meta.glob<{ default: Component }>('./items/**/*.vue', { eager: true })
const itemComponents: Record<string, Component> = {}

for (const [path, module] of Object.entries(itemModules)) {
  const componentName = path.split('/').pop()?.replace('.vue', '').toUpperCase()
  if (componentName) {
    itemComponents[componentName] = module.default
  }
}

function getFieldComponent(name: string) {
  return itemComponents[name.toUpperCase()]
}

const props = defineProps<{
  modelValue: DynamicFormValue
  formField: FormField
  view: boolean
  otherParams: Dict<DynamicFormValue>
  initDefaultData: (formField: FormField) => void
  defaultItemWidth: string
  formValue: Dict<DynamicFormValue>
  formFieldList: FormField[]
  parentField?: string
}>()

const emit = defineEmits<{ change: [value: DynamicFormValue]; 'change-label': [value: DynamicFormValue] }>()

const componentFormRef = ref<DynamicFieldComponent>()

function isString(value: unknown): value is string {
  return typeof value === 'string'
}

const fieldLabel = computed<FormFieldLabel | undefined>(() => {
  return isString(props.formField.label) ? undefined : props.formField.label
})

const labelValue = computed({
  get: () => {
    const field = fieldLabel.value?.field
    return field ? props.formValue[field] : undefined
  },
  set: (value: DynamicFormValue) => {
    if (fieldLabel.value?.field) {
      emit('change-label', value)
    }
  },
})

const itemValue = computed({
  get: () => props.modelValue,
  set: (value: DynamicFormValue) => {
    emit('change', value)
  },
})

const labelAttrs = computed(() => sanitizeFieldAttrs(fieldLabel.value?.attrs))
const fieldProps = computed(() => props.formField.props_info ?? {})
const formItemStyle = computed(() => fieldProps.value.item_style ?? {})
const componentStyle = computed(() => fieldProps.value.style ?? {})
const fieldAttrs = computed(() => sanitizeFieldAttrs(props.formField.attrs))

const errorMessage = computed(() => {
  if (fieldProps.value.err_msg) {
    return fieldProps.value.err_msg
  }
  const label = isString(props.formField.label) ? props.formField.label : props.formField.label?.label
  const messageKey = isSelectionFieldType(props.formField.input_type)
    ? 'common.validation.selectFieldRequired'
    : 'common.validation.inputFieldRequired'
  return t(messageKey, { label: label || props.formField.field })
})

const componentValidator: FormItemRule['validator'] = (rule, value, callback) => {
  if (componentFormRef.value?.validateRules) {
    return componentFormRef.value.validateRules(rule, value, callback)
  }
  callback()
}

// 字符串校验器不执行其内容，统一委托字段组件校验，避免存储型 XSS。
function deserializeRule(rule: SerializedFormRule): FormItemRule {
  if (typeof rule.validator !== 'string') {
    return rule as FormItemRule
  }
  return { ...rule, validator: componentValidator } as FormItemRule
}

const validationRules = computed<FormItemRule | FormItemRule[]>(() => {
  if (props.formField.input_type === 'LocalFileUpload') {
    // 文件字段在提交时校验，错误统一由 MkDynamicsForm 使用 MsgWarning 提示。
    const uploadRules: FormItemRule[] = [
      {
        required: props.formField.required !== false,
        validator: (_rule, value, callback) => {
          const message = getUploadValidationMessage(Array.isArray(value) ? value : [], props.formField.required !== false)
          callback(message ? new Error(message) : undefined)
        },
      },
      ...(fieldProps.value.rules?.map(deserializeRule) ?? []),
    ]
    return uploadRules.map((rule) => ({ ...rule, trigger: [] }))
  }
  if (fieldProps.value.rules) {
    return fieldProps.value.rules.map(deserializeRule)
  }
  return {
    message: errorMessage.value,
    required: props.formField.required !== false,
    ...(['TextInput', 'TextareaInput'].includes(props.formField.input_type) ? { whitespace: true } : {}),
    trigger: props.formField.input_type === 'Slider' ? 'blur' : ['blur', 'change'],
  }
})

onMounted(() => {
  props.initDefaultData(props.formField)
})

function validate() {
  if (props.formField.trigger_type === 'CHILD_FORMS') {
    return componentFormRef.value?.validate?.() ?? Promise.resolve()
  }
  return Promise.resolve()
}

defineExpose({ validate })
</script>

<template>
  <el-form-item
    :style="formItemStyle"
    :prop="formField.field"
    :rules="validationRules"
    :show-message="formField.input_type !== 'LocalFileUpload'"
    :class="fieldLabel && getFieldComponent(fieldLabel.input_type) ? 'mk-hide-asterisk' : ''"
  >
    <template v-if="formField.label" #label>
      <FormItemLabel v-if="isString(formField.label)" :form-field="formField" />
      <component
        :is="getFieldComponent(fieldLabel.input_type)"
        v-else-if="fieldLabel && getFieldComponent(fieldLabel.input_type)"
        v-model="labelValue"
        :label="fieldLabel"
        :form-value="formValue"
        v-bind="labelAttrs"
        :required="formField.required !== false"
      />
    </template>
    <component
      :is="getFieldComponent(formField.input_type)"
      v-if="getFieldComponent(formField.input_type)"
      ref="componentFormRef"
      v-model="itemValue"
      :view="view"
      :form-field="formField"
      :other-params="otherParams"
      :style="componentStyle"
      :field="formField.field"
      :formfield-list="formFieldList"
      v-bind="fieldAttrs"
    />
  </el-form-item>
</template>

<style lang="scss" scoped></style>
