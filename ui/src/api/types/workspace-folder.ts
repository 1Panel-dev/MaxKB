/** Workspace 下多个资源模块共用的文件夹业务类型。 */

export const FOLDER_SOURCE = {
  APPLICATION: 'APPLICATION',
  KNOWLEDGE: 'KNOWLEDGE',
  TOOL: 'TOOL',
} as const

export type FolderSource = (typeof FOLDER_SOURCE)[keyof typeof FOLDER_SOURCE]

export interface WorkspaceFolder {
  children?: WorkspaceFolder[]
  create_time?: string
  desc?: string | null
  id: string
  name: string
  parent_id?: string | null
  update_time?: string
  user_id?: string | null
  workspace_id: string
}

export interface WorkspaceFolderCreatePayload {
  desc?: string | null
  name: string
  parent_id?: string | null
}

export interface WorkspaceFolderUpdatePayload {
  desc?: string | null
  name?: string
  parent_id?: string | null
}

export interface WorkspaceFolderQuery {
  name?: string
  [key: string]: unknown
}
