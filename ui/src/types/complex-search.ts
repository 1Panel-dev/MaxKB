export type ComplexSearchValue = boolean | number | string

export interface ComplexSearchSelectOption {
  disabled?: boolean
  label: string
  value: ComplexSearchValue
}

export interface ComplexSearchFieldOption {
  label: string
  options?: ComplexSearchSelectOption[]
  type?: 'input' | 'select'
  value: string
}
