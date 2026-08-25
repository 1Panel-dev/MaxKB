interface LeftOptions {
  label: string
  value: string
  icon?: any
  type?: string
  self?: boolean
  children?: Array<LeftOptions>
  /**
   * 叶子字段配置,供 visibility 推断运算符与值编辑器
   */
  input_type?: string
  option_list?: Array<any>
  attrs?: Record<string, any>
}
export { type LeftOptions }
