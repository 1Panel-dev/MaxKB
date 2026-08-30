import type { CSSProperties } from 'vue'
import type { Dict } from '@/api/types'

/**
 * 动态表单协议允许字段组件携带不同结构的值。
 * 保留宽类型以兼容现有字段实现，具体组件应在边界处收窄。
 */
// eslint-disable-next-line @typescript-eslint/no-explicit-any
export type DynamicFormValue = any

export type DynamicFormValidatorCallback = (error?: string | Error) => void

export interface DynamicFormResponse<T> {
  data: T
}

export type DynamicFormSource = string | FormField[] | Promise<FormField[] | DynamicFormResponse<FormField[]>> | (() => Promise<FormField[] | DynamicFormResponse<FormField[]>>)

export type VisibilityCompareOperator = 'eq' | 'not_eq' | 'contain' | 'not_contain' | 'is_true' | 'is_not_true' | 'gt' | 'ge' | 'lt' | 'le'

export interface VisibilityCondition {
  id: string
  field: [scope: string, field: string]
  self?: boolean
  compare: VisibilityCompareOperator | ''
  value: DynamicFormValue
  leftValue?: DynamicFormValue
}

export interface VisibilityConditionState extends VisibilityCondition {
  _fieldError?: string
  _compareError?: string
  _valueError?: string
  _fieldType?: string
  _ops?: Array<{ label: string; value: string }>
  _options?: Dict<DynamicFormValue>[]
  _treeData?: DynamicFormValue[]
  _treeMultiple?: boolean
}

export interface VisibilityRules {
  action: 'show' | 'hide'
  condition: 'and' | 'or'
  conditions: VisibilityCondition[]
}

export interface DynamicFormTriggerSetting extends Dict<DynamicFormValue> {
  change?: string
  change_field?: string
  request?: string
  url?: string
  values?: DynamicFormValue[]
}

export type DynamicFormTriggerMap = Dict<DynamicFormTriggerSetting>

export interface FormFieldLabel extends Dict<DynamicFormValue> {
  attrs?: FormFieldAttributes
  field?: string
  input_type: string
  label?: string
  props_info?: FormFieldProps
  relation_trigger_field_dict?: DynamicFormTriggerMap
}

export interface FormViewCardItem {
  type: 'eval' | 'default'
  title: string
  value_field: string
}

export interface FormTableColumn {
  property: string
  label: string
  value_field?: string
  attrs?: FormFieldAttributes
  type: 'eval' | 'component' | 'default'
  props_info?: FormFieldProps
}

export interface FormProgressColor {
  color: string
  percentage: number
}

export interface FormFieldAttributes extends Dict<DynamicFormValue> {
  placeholder?: string
  labelWidth?: string
  labelSuffix?: string
  requireAsteriskPosition?: 'left' | 'right'
  color?: FormProgressColor[]
}

export interface SerializedFormRule extends Dict<DynamicFormValue> {
  validator?: string | ((...args: DynamicFormValue[]) => void)
}

export interface FormFieldProps extends Dict<DynamicFormValue> {
  view_card?: FormViewCardItem[]
  table_columns?: FormTableColumn[]
  active_msg?: string
  style?: CSSProperties
  item_style?: CSSProperties
  rules?: SerializedFormRule[]
  err_msg?: string
  tabs_label?: string
}

export interface FormField extends Dict<DynamicFormValue> {
  field: string
  input_type: string
  label?: string | FormFieldLabel
  required?: boolean
  default_value?: DynamicFormValue
  show_default_value?: boolean
  visibility_rules?: VisibilityRules | null
  relation_trigger_field_dict?: DynamicFormTriggerMap
  trigger_type?: 'OPTION_LIST' | 'CHILD_FORMS'
  attrs?: FormFieldAttributes
  props_info?: FormFieldProps
  text_field?: string
  value_field?: string
  option_list?: Dict<DynamicFormValue>[]
  provider?: string
  method?: string
  children?: FormField[]
  required_asterisk?: boolean
}

export interface DynamicFormConstructorState extends Dict<DynamicFormValue> {
  label: string
  field: string
  tooltip: string
  required: boolean
  input_type: string
  default_value?: DynamicFormValue
  show_default_value?: boolean
}

export interface DynamicFormConstructorOption {
  label: string
  value: string
}

export interface DynamicFormConstructorExpose {
  getData: () => Partial<FormField>
  render: (field: FormField) => void
  validate?: () => Promise<unknown>
}

export interface VisibilityFieldOption {
  label: string
  value: string
  icon?: DynamicFormValue
  type?: string
  self?: boolean
  children?: VisibilityFieldOption[]
  input_type?: string
  option_list?: Dict<DynamicFormValue>[]
  attrs?: FormFieldAttributes
}
