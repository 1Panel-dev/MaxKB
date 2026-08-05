/** 可过滤下拉组件使用的公共选项类型。 */

export interface DropdownOption {
  label: string
  value: string | number
  [key: string]: unknown
}
