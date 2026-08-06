/** 多个公共下拉组件共同使用的最小选项约束。 */

export interface OptionItem {
  label: string
  value: string | number
  [key: string]: unknown
}
