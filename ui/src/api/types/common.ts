/** 键为字符串的通用字典类型。 */
export type Dict<T> = Record<string, T>

/** 通用的 ID + 名称选项，用于下拉列表、标签等场景。 */
export interface ListItem {
  id: string
  name: string
  [key: string]: unknown
}

export interface OptionItem<Value extends boolean | number | string = string | number> {
  disabled?: boolean
  label: string
  options?: OptionItem<boolean | number | string>[]
  value: Value
  [key: string]: unknown
}

export interface ExportError {
  response: { status: number; data: Blob }
}

export interface CommonUserOption {
  id: string
  nick_name: string
  roles?: string[]
}


export interface DynamicFormField {
  attrs?: Record<string, unknown>
  default_value?: unknown
  field: string
  input_type: string
  label: string | DynamicFormLabel
  option_list?: Record<string, unknown>[]
  required?: boolean
  text_field?: string
  value_field?: string
  [key: string]: unknown
}

export interface DynamicFormLabel {
  attrs?: { tooltip?: string; [key: string]: unknown }
  input_type: string
  label: string
  type?: string
}
