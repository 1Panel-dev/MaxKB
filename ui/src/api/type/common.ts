export interface Dict<V> {
  [propName: string]: V
}

export interface KeyValue<K, V> {
  key: K
  value: V
}

export interface FormField {
  field: string
  input_type: string
  label?: string | any
  required?: boolean
  default_value?: any
  show_default_value?: boolean
  relation_show_field_dict?: Dict<Array<any>>
  relation_trigger_field_dict?: Dict<any>
  trigger_type?: 'OPTION_LIST' | 'CHILD_FORMS'
  attrs?: Record<string, any>
  props_info?: Record<string, any>
  text_field?: string
  value_field?: string
  option_list?: Array<any>
  provider?: string
  method?: string
  children?: Array<FormField>
  required_asterisk?: boolean
}

export interface PageList<T> {
  current: number
  size: number
  total: number
  records: T
}
