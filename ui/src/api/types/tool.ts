/** Workspace 工具列表和工具维护共用的业务类型。 */

import type LogicFlow from '@logicflow/core'
import { TOOL_SCOPE, TOOL_TYPE } from '@/api/enums'
import type { DynamicFormField } from './common'

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

export interface ToolDebugField extends ToolInputField {
  value: string
}

export interface ToolDebugPayload {
  code: string
  debug_field_list: ToolDebugField[]
  init_field_list: DynamicFormField[]
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
  fileList?: ToolFile[]
  icon?: string
  id: string
  init_field_list?: DynamicFormField[]
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
  work_flow?: LogicFlow.GraphConfigData
  workspace_id: string
}

export interface ToolWorkflowDetail {
  create_time?: string
  id: string
  is_publish: boolean
  publish_time?: string | null
  tool: string
  update_time?: string
  work_flow: LogicFlow.GraphConfigData
  workspace_id: string
}

export interface ToolFile {
  name: string
  size?: number
  uid?: number | string
}

export interface ToolPayload {
  code?: string
  desc?: string | null
  folder_id?: string | null
  icon?: string
  init_field_list?: DynamicFormField[]
  init_params?: Record<string, unknown> | null
  input_field_list?: ToolInputField[]
  is_active?: boolean
  name?: string
  scope?: ToolScope
  tool_type?: ToolType
  work_flow?: LogicFlow.GraphConfigData
  work_flow_template?: ToolStoreItem
}

export interface ToolStoreVersion {
  downloadUrl: string
  name: string
}

export interface ToolStoreTag {
  key: string
  name: string
}

export type ToolStoreSource = 'internal' | 'store'

export interface ToolStoreItem {
  desc?: string | null
  description?: string | null
  downloadCallbackUrl?: string
  downloadUrl?: string
  downloads?: number
  icon?: string
  id: string
  label?: string | null
  name: string
  readMe?: string
  source: ToolStoreSource
  tags?: string[]
  tool_type: ToolType
  version?: string | null
  versions?: ToolStoreVersion[]
}

export interface ToolStoreResponse {
  additionalProperties: { tags: ToolStoreTag[] }
  apps: Omit<ToolStoreItem, 'source' | 'tool_type'>[]
}

export interface AddInternalToolPayload {
  folder_id: string
  name: string
}

export interface AddStoreToolPayload extends AddInternalToolPayload {
  download_callback_url: string
  download_url: string
  icon: string
  label: string
  versions: ToolStoreVersion[]
}

export interface UpdateStoreToolPayload {
  download_callback_url: string
  download_url: string
  icon: string
  label: string
  versions: ToolStoreVersion[]
}
