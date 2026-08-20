/** Workspace 工具列表和工具维护共用的业务类型。 */

import { TOOL_SCOPE, TOOL_TYPE } from '@/api/enums'

export type ToolScope = (typeof TOOL_SCOPE)[keyof typeof TOOL_SCOPE]
export type ToolType = (typeof TOOL_TYPE)[keyof typeof TOOL_TYPE]

export interface WorkspaceTool {
  code?: string
  create_time?: string
  desc?: string | null
  folder_id?: string
  icon?: string
  id: string
  init_field_list?: Record<string, unknown>[]
  init_params?: Record<string, unknown> | string | null
  input_field_list?: Record<string, unknown>[]
  is_active: boolean
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
  init_field_list?: Record<string, unknown>[]
  init_params?: Record<string, unknown> | null
  input_field_list?: Record<string, unknown>[]
  is_active?: boolean
  name?: string
  scope?: ToolScope
  tool_type?: ToolType
}
