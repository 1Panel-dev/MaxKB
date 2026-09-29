export type StatusLabelType = 'success' | 'failure' | 'loading' | 'disabled'

export interface StatusLabelOptions {
  type: StatusLabelType
  label: string
}
