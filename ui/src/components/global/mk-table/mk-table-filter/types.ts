import type { CascaderValue, CheckboxValueType } from 'element-plus'

export interface TableFilterOption {
  label: string
  value: CheckboxValueType
  disabled?: boolean
}

export type TableFilterValue = CascaderValue | CheckboxValueType | CheckboxValueType[] | null | undefined
