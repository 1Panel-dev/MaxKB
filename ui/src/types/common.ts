/** 多个公共组件共同使用的通用选项类型。 */

export interface OptionItem<Value extends boolean | number | string = string | number> {
  disabled?: boolean
  label: string
  options?: OptionItem<boolean | number | string>[]
  value: Value
  [key: string]: unknown
}

export interface List {
  id: string
  name: string
  [key: string]: unknown
}
