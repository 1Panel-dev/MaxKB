/** Workspace 模型与工具页面共用的业务类型。 */

export const MODEL_STATUS = {
  DOWNLOAD: 'DOWNLOAD',
  ERROR: 'ERROR',
  PAUSE_DOWNLOAD: 'PAUSE_DOWNLOAD',
  SUCCESS: 'SUCCESS',
} as const

export type ModelStatus = (typeof MODEL_STATUS)[keyof typeof MODEL_STATUS]

export interface ModelProvider {
  icon: string
  name: string
  provider: string
}

export interface WorkspaceModel {
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

export interface ModelListQuery {
  create_user?: string
  model_name?: string
  model_type?: string
  name?: string
  provider?: string
  [key: string]: unknown
}

export interface SelectableModelResponse {
  model: WorkspaceModel[]
  shared_model: WorkspaceModel[]
}

export interface ModelPayload {
  credential: Record<string, unknown>
  model_name: string
  model_type: string
  name: string
  provider: string
}

export interface DynamicFormField {
  default_value?: unknown
  field: string
  label: string
  required?: boolean
  [key: string]: unknown
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

export type ToolType = 'CUSTOM' | 'DATA_SOURCE' | 'INTERNAL' | 'MCP' | 'SKILL' | 'WORKFLOW'

export interface WorkspaceTool {
  create_time?: string
  desc?: string
  folder_id?: string
  icon?: string
  id: string
  is_active: boolean
  name: string
  nick_name?: string
  scope?: 'SHARED' | 'WORKSPACE'
  source?: 'shared' | 'workspace'
  tool_type: ToolType
  version?: string
  [key: string]: unknown
}

export interface ToolFolder {
  children?: ToolFolder[]
  create_time?: string
  desc?: string
  id: string
  name: string
  parent_id?: string
  update_time?: string
  user_id?: string
  workspace_id: string
}

export interface ToolListQuery {
  create_user?: string
  folder_id?: string
  name?: string
  scope?: 'SHARED' | 'WORKSPACE'
  tool_type?: ToolType | ''
  [key: string]: unknown
}

export interface ToolTreeResponse {
  folders: ToolFolder[]
  tools: WorkspaceTool[]
}

export interface ToolCatalogResponse {
  shared_tools: WorkspaceTool[]
  tools: WorkspaceTool[]
}

export interface ToolPayload {
  code?: string
  desc?: string
  folder_id?: string
  icon?: string
  input_field_list?: unknown[]
  is_active?: boolean
  name?: string
  tool_type?: ToolType
  [key: string]: unknown
}

export interface ToolFolderPayload {
  desc?: string
  name: string
  parent_id?: string
}

export interface AddStoreToolPayload {
  folder_id: string
  name: string
  [key: string]: unknown
}
