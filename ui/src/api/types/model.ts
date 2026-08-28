/** Workspace 模型与工具页面共用的业务类型。 */

import { MODEL_STATUS } from '@/api/enums'

export type ModelStatus = (typeof MODEL_STATUS)[keyof typeof MODEL_STATUS]

export interface ModelProviderItem {
  icon: string
  name: string
  provider: string
}

export interface ModelItem {
  create_time?: string
  id: string
  meta?: Record<string, unknown>
  model_name: string
  model_type: string
  name: string
  nick_name?: string
  provider: string
  source?: 'shared' | 'workspace'
  status: ModelStatus
  user_id?: string
  username?: string
  workspace_id?: string
}

export interface WorkspaceUserOption {
  id: string
  nick_name: string
}

export interface ModelPayload {
  credential: Record<string, unknown>
  model_name: string
  model_params_form?: DynamicFormField[]
  model_type: string
  name: string
  provider: string
}

export interface DynamicFormField {
  attrs?: Record<string, unknown>
  default_value?: unknown
  field: string
  input_type: string
  label: string | DynamicFormLabel
  option_list?: Record<string, unknown>[]
  required?: boolean
  text_field?: string
  value_field?: string
  [key: string]: unknown
}

export interface DynamicFormLabel {
  attrs?: {
    tooltip?: string
    [key: string]: unknown
  }
  input_type: string
  label: string
  type?: string
}

export interface BaseModelOption {
  desc?: string
  model_type: string
  name: string
}

export interface ModelTypeOption {
  key: string
  value: string
}
