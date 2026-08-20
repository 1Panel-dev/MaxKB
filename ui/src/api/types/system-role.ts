import { ROLE_TYPE } from '@/api/enums'

export type RoleType = (typeof ROLE_TYPE)[keyof typeof ROLE_TYPE]

export interface RoleItem {
  id: string
  role_name: string
  type: RoleType
  create_user: string
  internal: boolean
  user_count?: number
}

export interface RolePermission {
  id: string
  name: string
  enable: boolean
}

export interface RolePermissionFeature {
  id: string
  name: string
  enable: boolean
  permission: RolePermission[]
}

export interface RolePermissionModule {
  id: string
  name: string
  children: RolePermissionFeature[]
}

export interface RolePayload {
  role_id?: string
  role_name: string
  role_type?: RoleType
}

export interface SaveRolePermissionRequest {
  id: string
  enable: boolean
}

export interface RoleMember {
  user_relation_id: string
  user_id: string
  username: string
  nick_name: string
  workspace_id: string
  workspace_name: string
}

export interface CreateRoleMemberItem {
  user_ids: string[]
  workspace_ids?: string[]
}

export interface CreateRoleMembersRequest {
  members: CreateRoleMemberItem[]
}
