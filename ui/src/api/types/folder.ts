/** Workspace 下多个资源模块共用的文件夹业务类型。 */

import { FOLDER_SOURCE } from '@/api/enums'

export type FolderSource = (typeof FOLDER_SOURCE)[keyof typeof FOLDER_SOURCE]

export interface FolderItem {
  children?: FolderItem[]
  create_time?: string
  desc?: string | null
  id: string
  name: string
  parent_id?: string | null
  update_time?: string
  user_id?: string | null
  workspace_id?: string
}

export interface FolderPayload {
  desc?: string | null
  name?: string
  parent_id?: string | null
}
