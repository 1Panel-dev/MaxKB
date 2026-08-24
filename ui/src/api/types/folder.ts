/** Workspace 下多个资源模块共用的文件夹业务类型。 */

import { RESOURCE_TYPE } from '@/api/enums'
import type { ResourceType } from './resource-authorization'

/** 文件夹接口支持的资源类型，不包含没有文件夹层级的模型。 */
export type FolderSource = Exclude<ResourceType, typeof RESOURCE_TYPE.MODEL>

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
