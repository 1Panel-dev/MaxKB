export interface ToolOutputField {
  field: string
  label: string
  name?: string
  type?: string
  is_required?: boolean
}

export interface ToolInputField extends ToolOutputField {
  type: string
  desc: string
  is_required: boolean
}

export interface ToolFieldConfig {
  title: string
}
