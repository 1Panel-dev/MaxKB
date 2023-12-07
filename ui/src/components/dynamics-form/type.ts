import type { Dict } from '@/api/type/common'

interface ViewCardItem {
  /**
   * 类型
   */
  type: 'eval' | 'default'
  /**
   * 标题
   */
  title: string
  /**
   * 值 根据类型不一样 取值也不一样 default= row[value_field] eval `${parseFloat(row.number).toLocaleString("zh-CN",{style: "decimal",maximumFractionDigits:1})}%&nbsp;&nbsp;&nbsp;`
   */
  value_field: string
}

interface TableColumn {
  /**
   * 字段|组件名称|可计算的模板字符串
   */
  property: string
  /**
   *表头
   */
  label: string
  /**
   * 表数据字段
   */
  value_field?: string

  attrs?: Attrs
  /**
   * 类型
   */
  type: 'eval' | 'component' | 'default'

  props_info?: PropsInfo
}
interface ColorItem {
  /**
   * 颜色#f56c6c
   */
  color: string
  /**
   * 进度
   */
  percentage: number
}
interface Attrs {
  /**
   * 提示语
   */
  placeholder?: string
  /**
   * 标签的长度，例如 '50px'。 作为 Form 直接子元素的 form-item 会继承该值。 可以使用 auto。
   */
  labelWidth?: string
  /**
   * 表单域标签的后缀
   */
  labelSuffix?: string
  /**
   * 星号的位置。
   */
  requireAsteriskPosition?: 'left' | 'right'

  color?: Array<ColorItem>

  [propName: string]: any
}
interface PropsInfo {
  /**
   * 表格选择的card
   */
  view_card?: Array<ViewCardItem>
  /**
   * 表格选择
   */
  table_columns?: Array<TableColumn>
  /**
   * 选中 message
   */
  active_msg?: string

  /**
   * 组件样式
   */
  style?: Dict<any>

  /**
   * el-form-item 样式
   */
  item_style?: Dict<any>
  /**
   * 表单校验 这个和element校验一样
   */
  rules?: Dict<any>
  /**
   * 默认 不为空校验提示
   */
  err_msg?: string
  /**
   *tabs的时候使用
   */
  tabs_label?: string

  [propName: string]: any
}

interface FormField {
  field: string
  /**
   * 输入框类型
   */
  input_type: string
  /**
   * 提示
   */
  label?: string
  /**
   * 是否 必填
   */
  required?: boolean
  /**
   * 默认值
   */
  default_value?: any
  /**
   *  {field:field_value_list} 表示在 field有值 ,并且值在field_value_list中才显示
   */
  relation_show_field_dict?: Dict<Array<any>>
  /**
   * {field:field_value_list} 表示在 field有值 ,并且值在field_value_list中才 执行函数获取 数据
   */
  relation_trigger_field_dict?: Dict<Array<any>>
  /**
   * 执行器类型  OPTION_LIST请求Option_list数据 CHILD_FORMS请求子表单
   */
  trigger_type?: 'OPTION_LIST' | 'CHILD_FORMS'
  /**
   * 前端attr数据
   */
  attrs?: Attrs
  /**
   * 其他额外信息
   */
  props_info?: PropsInfo
  /**
   * 下拉选字段field
   */
  text_field?: string
  /**
   * 下拉选 value
   */
  value_field?: string
  /**
   * 下拉选数据
   */
  option_list?: Array<any>
  /**
   * 供应商
   */
  provider?: string
  /**
   * 执行函数
   */
  method?: string

  children?: Array<FormField>
}
export type { FormField }
