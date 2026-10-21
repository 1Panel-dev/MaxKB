export type StatusLabelType = 'success' | 'failure' | 'loading' | 'disabled' | 'custom'

export interface StatusLabelOptions {
  type: StatusLabelType
  label: string
  icon?: string
}
