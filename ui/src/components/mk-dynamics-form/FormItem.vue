<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted, ref, type Component, type Ref } from 'vue'
import type { FormItemRule } from 'element-plus'
import { get } from 'lodash'
import type { Dict } from '@/api/types'
import bus from '@/utils/bus'
import FormItemLabel from './FormItemLabel.vue'
import type {
  DynamicFormTriggerMap,
  DynamicFormTriggerSetting,
  DynamicFormValue,
  FormField,
  FormFieldLabel,
  SerializedFormRule,
} from './type'

defineOptions({ name: 'MkDynamicsFormItem' })

interface DynamicFieldComponent {
  validate?: () => Promise<unknown>
}

const itemModules = import.meta.glob<{ default: Component }>('./items/**/*.vue', { eager: true })
const itemComponents: Record<string, Component> = {}

for (const [path, module] of Object.entries(itemModules)) {
  const componentName = path.split('/').pop()?.replace('.vue', '')
  if (componentName) {
    itemComponents[componentName] = module.default
  }
}

function getFieldComponent(name: string) {
  return itemComponents[name]
}

const props = defineProps<{
  modelValue: DynamicFormValue
  formField: FormField
  view: boolean
  otherParams: Dict<DynamicFormValue>
  trigger: (
    triggerField: string,
    triggerValue: DynamicFormValue,
    triggerSetting: DynamicFormTriggerSetting,
    target: Dict<DynamicFormValue>,
    loading: Ref<boolean>,
  ) => void
  initDefaultData: (formField: FormField) => void
  defaultItemWidth: string
  formValue: Dict<DynamicFormValue>
  formFieldList: FormField[]
  parentField?: string
}>()

const emit = defineEmits<{
  change: [value: DynamicFormValue]
  'change-label': [value: DynamicFormValue]
}>()

const loading = ref(false)
const fieldComponentRef = ref<DynamicFieldComponent>()
const triggerSubscriptions: Array<{
  event: string
  handler: (value: unknown) => void
}> = []

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
    const field = fieldLabel.value?.field
    if (!field) {
      return
    }
    emit('change-label', value)
    bus.emit(field, value)
  },
})

const itemValue = computed({
  get: () => props.modelValue,
  set: (value: DynamicFormValue) => {
    emit('change', value)
    const eventName = props.parentField
      ? `${props.parentField}.${props.formField.field}`
      : props.formField.field
    bus.emit(eventName, value)
  },
})

const labelAttrs = computed(() => fieldLabel.value?.attrs ?? {})
const fieldProps = computed(() => props.formField.props_info ?? {})
const formItemStyle = computed(() => fieldProps.value.item_style ?? {})
const componentStyle = computed(() => fieldProps.value.style ?? {})
const fieldAttrs = computed(() => props.formField.attrs ?? {})

const errorMessage = computed(() => {
  if (fieldProps.value.err_msg) {
    return fieldProps.value.err_msg
  }
  const label = isString(props.formField.label)
    ? props.formField.label
    : props.formField.label?.label
  return `${label || props.formField.field} 不能为空`
})

function deserializeRule(rule: SerializedFormRule): FormItemRule {
  if (typeof rule.validator !== 'string') {
    return rule as FormItemRule
  }

  let validator: FormItemRule['validator']
  // 动态校验器来自受信任的服务端字段协议。
  eval(rule.validator)
  return { ...rule, validator } as FormItemRule
}

const validationRules = computed<FormItemRule | FormItemRule[]>(() => {
  if (fieldProps.value.rules) {
    return fieldProps.value.rules.map(deserializeRule)
  }
  return {
    message: errorMessage.value,
    required: props.formField.required !== false,
    trigger: props.formField.input_type === 'Slider' ? 'blur' : ['blur', 'change'],
  }
})

function executeInitialTriggers(
  target: Dict<DynamicFormValue>,
  triggerMap?: DynamicFormTriggerMap,
) {
  if (!triggerMap) {
    return
  }

  for (const [event, setting] of Object.entries(triggerMap)) {
    const triggerValue = get(props.formValue, event)
    if (!setting.values?.length || setting.values.includes(triggerValue)) {
      props.trigger(event, triggerValue, setting, target, loading)
    }
  }
}

function subscribeToTriggers(target: Dict<DynamicFormValue>, triggerMap?: DynamicFormTriggerMap) {
  if (!triggerMap) {
    return
  }

  for (const [event, setting] of Object.entries(triggerMap)) {
    const handler = (value: unknown) => {
      if (!setting.values?.length || setting.values.includes(value)) {
        props.trigger(event, value, setting, target, loading)
      }
    }
    bus.on(event, handler)
    triggerSubscriptions.push({ event, handler })
  }
}

onMounted(() => {
  props.initDefaultData(props.formField)
  executeInitialTriggers(props.formField, props.formField.relation_trigger_field_dict)
  subscribeToTriggers(props.formField, props.formField.relation_trigger_field_dict)

  if (fieldLabel.value) {
    executeInitialTriggers(fieldLabel.value, fieldLabel.value.relation_trigger_field_dict)
    subscribeToTriggers(fieldLabel.value, fieldLabel.value.relation_trigger_field_dict)
  }
})

onBeforeUnmount(() => {
  for (const { event, handler } of triggerSubscriptions) {
    bus.off(event, handler)
  }
})

function validate() {
  if (props.formField.trigger_type === 'CHILD_FORMS') {
    return fieldComponentRef.value?.validate?.() ?? Promise.resolve()
  }
  return Promise.resolve()
}

defineExpose({ validate })
</script>

<template>
  <el-form-item
    v-loading="loading"
    :key="formField.field"
    :style="formItemStyle"
    :prop="formField.field"
    :rules="validationRules"
    :class="formField.required_asterisk ? 'hide-asterisk' : ''"
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
      />
    </template>
    <component
      :is="getFieldComponent(formField.input_type)"
      v-if="getFieldComponent(formField.input_type)"
      ref="fieldComponentRef"
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
