/** 系统资源授权 API 与页面共用的业务类型。 */

import { RESOURCE_TYPE, RESOURCE_PERMISSION } from '@/api/enums'
import type { ToolType } from './tool'

export type ResourceType = (typeof RESOURCE_TYPE)[keyof typeof RESOURCE_TYPE]
export type ResourceAuthorizationType = ResourceType
export type ResourcePermission = (typeof RESOURCE_PERMISSION)[keyof typeof RESOURCE_PERMISSION]

export interface ResourcePermissionItem {
  auth_target_type: ResourceAuthorizationType
  children?: ResourcePermissionItem[]
  folder_id: string | null
  icon?: string | null
  id: string
  name: string
  permission: ResourcePermission
  resource_type: 'application' | 'folder' | 'knowledge' | 'model' | 'tool'
  tool_type?: ToolType | null
  user_id: string
  workspace_id: string
}

export interface ResourcePermissionPayload {
  permission: ResourcePermission
  target_id: string
}
