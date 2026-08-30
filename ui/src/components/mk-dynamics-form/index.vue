<script setup lang="ts">
import { computed, nextTick, onBeforeMount, ref, watch, type Ref } from 'vue'
import type { FormInstance } from 'element-plus'
import { cloneDeep, isEqual } from 'lodash'
import { del, get, post, put } from '@/api/admin/core/request'
import type { Dict } from '@/api/types'
import FormItem from './FormItem.vue'
import type {
  DynamicFormResponse,
  DynamicFormSource,
  DynamicFormTriggerSetting,
  DynamicFormValue,
  FormField,
  VisibilityCompareOperator,
  VisibilityCondition,
  VisibilityRules,
} from './type'

defineOptions({ name: 'MkDynamicsForm' })

const props = withDefaults(
  defineProps<{
    /** 页面字段配置或字段配置加载器。 */
    renderData: DynamicFormSource
    /** 动态请求脚本使用的额外参数。 */
    otherParams?: Dict<DynamicFormValue>
    /** 是否只读。 */
    view?: boolean
    /** 单个表单项的默认宽度。 */
    defaultItemWidth?: string
    /** 嵌套表单的父字段路径。 */
    parentField?: string
    modelValue?: Dict<DynamicFormValue>
  }>(),
  { defaultItemWidth: '75%', modelValue: () => ({}), otherParams: () => ({}), view: false },
)

const emit = defineEmits<{ 'update:modelValue': [value: Dict<DynamicFormValue>] }>()

const request = { del, get, post, put }
const formValue = ref<Dict<DynamicFormValue>>(cloneDeep(props.modelValue))
const loading = ref(false)
const formFieldList = ref<FormField[]>([])
const ruleFormRef = ref<FormInstance>()
const formItemRefs = ref<InstanceType<typeof FormItem>[]>([])

// ===== 字段显隐 =====
function containsValue(source: DynamicFormValue, target: DynamicFormValue): boolean {
  if (Array.isArray(target)) {
    return target.every((targetItem) => containsValue(source, targetItem))
  }
  const normalizedTarget = String(target)
  if (typeof source === 'string') {
    return source.includes(normalizedTarget)
  }
  if (Array.isArray(source)) {
    return source.some((sourceItem) => String(sourceItem) === normalizedTarget)
  }
  return String(source).includes(normalizedTarget)
}

function compareNumberOrString(
  left: DynamicFormValue,
  right: DynamicFormValue,
  compareNumber: (left: number, right: number) => boolean,
  compareString: (left: string, right: string) => boolean,
): boolean {
  const leftNumber = Number(left)
  const rightNumber = Number(right)
  if (!Number.isNaN(leftNumber) && !Number.isNaN(rightNumber)) {
    return compareNumber(leftNumber, rightNumber)
  }
  return compareString(String(left), String(right))
}

const visibilityCompareHandlers: Record<VisibilityCompareOperator, (left: DynamicFormValue, right: DynamicFormValue) => boolean> = {
  contain: containsValue,
  eq: (left, right) => String(left) === String(right),
  ge: (left, right) =>
    compareNumberOrString(
      left,
      right,
      (a, b) => a >= b,
      (a, b) => a >= b,
    ),
  gt: (left, right) =>
    compareNumberOrString(
      left,
      right,
      (a, b) => a > b,
      (a, b) => a > b,
    ),
  is_not_true: (left) => left !== true,
  is_true: (left) => left === true,
  le: (left, right) =>
    compareNumberOrString(
      left,
      right,
      (a, b) => a <= b,
      (a, b) => a <= b,
    ),
  lt: (left, right) =>
    compareNumberOrString(
      left,
      right,
      (a, b) => a < b,
      (a, b) => a < b,
    ),
  not_contain: (left, right) => !containsValue(left, right),
  not_eq: (left, right) => String(left) !== String(right),
}

function getVisibilityConditionValue(condition: VisibilityCondition, values: Dict<DynamicFormValue>): DynamicFormValue {
  return condition.self ? values[condition.field[1]] : condition.leftValue
}

function evaluateVisibility(rules: VisibilityRules | null | undefined, values: Dict<DynamicFormValue>): boolean {
  if (!rules?.conditions.length) {
    return true
  }

  const results = rules.conditions.map((condition) => {
    if (!condition.compare) {
      return false
    }
    const leftValue = getVisibilityConditionValue(condition, values)
    if (leftValue == null && condition.compare !== 'is_true' && condition.compare !== 'is_not_true') {
      return false
    }
    return visibilityCompareHandlers[condition.compare](leftValue, condition.value)
  })
  const matches = rules.condition === 'or' ? results.some(Boolean) : results.every(Boolean)
  return rules.action === 'show' ? matches : !matches
}

const fieldVisibility = computed<Record<string, boolean>>(() => {
  const currentValues = { ...formValue.value }
  const visibility: Record<string, boolean> = {}

  for (const field of formFieldList.value) {
    const visible = evaluateVisibility(field.visibility_rules, currentValues)
    visibility[field.field] = visible
    if (!visible) {
      currentValues[field.field] = null
    }
  }
  return visibility
})

function isFieldVisible(field: FormField) {
  return fieldVisibility.value[field.field] ?? true
}

// ===== 表单值同步 =====
function changeFieldValue(field: FormField, value: DynamicFormValue) {
  formValue.value[field.field] = value
}

function changeFieldLabel(field: FormField, value: DynamicFormValue) {
  if (typeof field.label !== 'string' && field.label?.field) {
    formValue.value[field.label.field] = value
  }
}

watch(
  formValue,
  (value) => {
    emit('update:modelValue', value)
  },
  { deep: true },
)

watch(
  () => props.modelValue,
  (value) => {
    if (!isEqual(value, formValue.value)) {
      formValue.value = cloneDeep(value)
    }
  },
  { deep: true },
)

// ===== 动态字段请求 =====
function renderTemplate(template: string, data: Dict<DynamicFormValue>) {
  return template.replace(/\$\{(\w+)\}/g, (match, key: string) => {
    return data[key] === undefined ? match : String(data[key])
  })
}

function triggerFieldRequest(
  triggerField: string,
  triggerValue: DynamicFormValue,
  triggerSetting: DynamicFormTriggerSetting,
  target: Dict<DynamicFormValue>,
  requestLoading: Ref<boolean>,
) {
  const executeRequest = new Function('self', 'triggerSetting', 'request', 'extra', triggerSetting.request || 'return request.get(extra.renderTemplate(triggerSetting.url));') as (
    self: Dict<DynamicFormValue>,
    setting: DynamicFormTriggerSetting,
    requestHelpers: typeof request,
    extra: Dict<DynamicFormValue>,
  ) => Promise<DynamicFormValue>

  const requestPromise = executeRequest(target, triggerSetting, request, {
    loading: requestLoading,
    renderTemplate: (url: string) => renderTemplate(url, { trigger_value: triggerValue, ...props.otherParams }),
  })

  if (!triggerSetting.change && !triggerSetting.change_field) {
    return
  }

  void requestPromise.then((response) => {
    const applyResponse = new Function(
      'self',
      'triggerSetting',
      'response',
      'extra',
      triggerSetting.change ||
        `self[triggerSetting.change_field]=[
          ...response.data.shared_model.map((model) => ({ ...model, type: 'share' })),
          ...response.data.model.map((model) => ({ ...model, type: 'workspace' }))
        ];`,
    ) as (self: Dict<DynamicFormValue>, setting: DynamicFormTriggerSetting, response: DynamicFormValue, extra: Dict<DynamicFormValue>) => void

    applyResponse(target, triggerSetting, response, { formData: formValue.value, getDefault: getFormDefaultValue })
  })
}

function initializeFieldDefault(field: FormField) {
  const currentValue = formValue.value[field.field]
  if (field.show_default_value === true && (currentValue === undefined || currentValue === null) && field.default_value !== undefined) {
    formValue.value[field.field] = cloneDeep(field.default_value)
  }
}

function hasValidOptionValue(field: FormField, value: DynamicFormValue) {
  if (!field.value_field || !field.option_list?.length) {
    return true
  }
  const selectedValues = Array.isArray(value) ? value : [value]
  return selectedValues.every((selectedValue) => field.option_list?.some((option) => option[field.value_field as string] === selectedValue))
}

function getFormDefaultValue(fields: FormField[], initialValue: Dict<DynamicFormValue> = {}): Dict<DynamicFormValue> {
  const value = { ...initialValue }

  for (const field of fields) {
    const initialFieldValue = initialValue[field.field]
    if (initialFieldValue !== undefined && hasValidOptionValue(field, initialFieldValue)) {
      value[field.field] = initialFieldValue
    } else if (field.show_default_value !== false) {
      value[field.field] = cloneDeep(field.default_value)
    }
  }
  return value
}

function getResponseFields(response: FormField[] | DynamicFormResponse<FormField[]>): FormField[] {
  return Array.isArray(response) ? response : response.data
}

async function resolveFormFields(source: DynamicFormSource): Promise<FormField[]> {
  if (typeof source === 'string') {
    return get<FormField[]>(source, {}, loading)
  }
  if (Array.isArray(source)) {
    return source
  }
  const response = typeof source === 'function' ? await source() : await source
  return getResponseFields(response)
}

async function render(source: DynamicFormSource, data: Dict<DynamicFormValue> = {}) {
  formFieldList.value = []
  await nextTick()
  const fields = await resolveFormFields(source)
  formFieldList.value = fields
  formValue.value = cloneDeep(getFormDefaultValue(fields, data))
}

onBeforeMount(() => {
  void render(props.renderData, props.modelValue)
})

async function validate() {
  for (const field of formFieldList.value) {
    if (!isFieldVisible(field)) {
      formValue.value[field.field] = null
    }
  }

  return Promise.all([...formItemRefs.value.map((item) => item.validate()), ruleFormRef.value?.validate() ?? Promise.resolve()])
}

defineExpose({ initDefaultData: initializeFieldDefault, render, ruleFormRef, validate })
</script>

<template>
  <el-form ref="ruleFormRef" v-loading="loading" :model="formValue" label-position="top" require-asterisk-position="right" v-bind="$attrs" @submit.prevent>
    <slot :form-value="formValue" />
    <template v-for="field in formFieldList" :key="field.field">
      <FormItem
        v-if="isFieldVisible(field)"
        ref="formItemRefs"
        :model-value="formValue[field.field]"
        :form-field="field"
        :trigger="triggerFieldRequest"
        :view="view"
        :init-default-data="initializeFieldDefault"
        :default-item-width="defaultItemWidth"
        :other-params="otherParams"
        :form-value="formValue"
        :form-field-list="formFieldList"
        :parent-field="parentField"
        @change="changeFieldValue(field, $event)"
        @change-label="changeFieldLabel(field, $event)"
      />
    </template>
  </el-form>
</template>
