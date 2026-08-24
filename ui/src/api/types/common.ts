/** 多个公共组件共同使用的通用选项类型。 */
export type RequestParams = Record<string, unknown>

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
  response: {
    status: number
    data: Blob
  }
}

export interface CommonUserOption {
  id: string
  nick_name: string
  roles?: string[]
}
