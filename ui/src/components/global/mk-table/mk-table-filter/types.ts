import type { CascaderValue, CheckboxValueType } from 'element-plus'
import type { Dict } from '@/api/types'

export interface TableFilterOption {
  label: string
  value: CheckboxValueType
  disabled?: boolean
}

export type TableFilterCustomValue = Dict<unknown>

export type TableFilterValue = CascaderValue | CheckboxValueType | CheckboxValueType[] | TableFilterCustomValue | null | undefined
