/** Workspace 工具列表和工具维护共用的业务类型。 */

import { TOOL_SCOPE, TOOL_TYPE } from '@/api/enums'

export type ToolScope = (typeof TOOL_SCOPE)[keyof typeof TOOL_SCOPE]
export type ToolType = (typeof TOOL_TYPE)[keyof typeof TOOL_TYPE]

export type ToolInputFieldType = 'array' | 'dict' | 'float' | 'int' | 'string'
export type ToolInputFieldSource = 'custom' | 'reference'

export interface ToolInputField {
  desc?: string
  is_required: boolean
  name: string
  source: ToolInputFieldSource
  type: ToolInputFieldType
}

export interface ToolInitField {
  attrs?: Record<string, unknown>
  default_value?: unknown
  field: string
  input_type: string
  label: string
  option_list?: Record<string, unknown>[]
  props_info?: Record<string, unknown>
  required: boolean
  show_default_value?: boolean
}

export interface ToolDebugField extends ToolInputField {
  value: string
}

export interface ToolDebugPayload {
  code: string
  debug_field_list: ToolDebugField[]
  init_field_list: ToolInitField[]
  init_params: Record<string, unknown>
  input_field_list: ToolInputField[]
}

export interface ToolPylintIssue {
  column: number
  endColumn: number
  endLine: number
  line: number
  message: string
  module: string
  obj: string
  path: string
  symbol: string
  type: 'error' | 'warning'
}

export interface ToolItem {
  code?: string
  create_time?: string
  desc?: string | null
  folder_id?: string
  icon?: string
  id: string
  init_field_list?: ToolInitField[]
  init_params?: Record<string, unknown> | string | null
  input_field_list?: ToolInputField[]
  is_active: boolean
  is_publish?: boolean
  label?: string | null
  name: string
  nick_name?: string | null
  scope: ToolScope
  source?: 'shared' | 'workspace'
  template_id?: string | null
  tool_type: ToolType
  update_time?: string
  user_id?: string | null
  version?: string | null
  workspace_id: string
}

export interface ToolPayload {
  code?: string
  desc?: string | null
  folder_id?: string | null
  icon?: string
  init_field_list?: ToolInitField[]
  init_params?: Record<string, unknown> | null
  input_field_list?: ToolInputField[]
  is_active?: boolean
  name?: string
  scope?: ToolScope
  tool_type?: ToolType
}
