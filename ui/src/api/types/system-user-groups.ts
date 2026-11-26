import type { RoleInfo } from './system-role'

export interface SystemUserGroup {
  id: string
  name: string
  workspace_id: string
  count: number
}

export interface SystemUserGroupMember {
  id: string
  role_info?: RoleInfo[]
  roles: string[]
  username: string
  email: string
  phone: string
  is_active: boolean
  role: string
  nick_name: string
  create_time: string
  update_time: string
  source: string
  system_user_group_relation_id: string
}
