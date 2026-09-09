/** 系统资源授权 API 与页面共用的业务类型。 */

import { RESOURCE_TYPE, RESOURCE_PERMISSION, RESOURCE_AUTHORIZATION_TARGET_TYPE } from '@/api/enums'
import type { ToolType } from './tool'

export type ResourceType = (typeof RESOURCE_TYPE)[keyof typeof RESOURCE_TYPE]
export type ResourceAuthorizationType = ResourceType
export type ResourcePermission = (typeof RESOURCE_PERMISSION)[keyof typeof RESOURCE_PERMISSION]

export type ResourceAuthorizationTargetType = (typeof RESOURCE_AUTHORIZATION_TARGET_TYPE)[keyof typeof RESOURCE_AUTHORIZATION_TARGET_TYPE]

/** 指定资源下的用户及其权限，与用户视角的资源列表区分。 */
export interface ResourceUserPermission {
  id: string
  nick_name: string
  username: string
  role_name?: string[]
  permission: ResourcePermission
}

export interface ResourceUserPermissionPayload {
  user_id: string
  permission: ResourcePermission
  include_children?: boolean
  folder_ids?: string[]
}

/** 指定资源下的用户组及其权限。 */
export interface ResourceUserGroupPermission {
  id: string
  name: string
  count: number
  permission: ResourcePermission
}

export interface ResourceUserGroupPermissionPayload {
  user_group_id: string
  permission: ResourcePermission
  include_children?: boolean
  folder_ids?: string[]
}

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
