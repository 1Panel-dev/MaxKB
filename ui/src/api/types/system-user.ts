/** 系统用户 API 与用户管理页面共用的业务类型。 */

export interface SystemUserRoleAssignment {
  role_id: string
  workspace_ids: string[]
}

export interface BatchSetUserRolesRequest {
  ids: string[]
  is_append: boolean
  role_ids: string[]
}

export interface BatchSetUserWorkspaceRolesRequest {
  ids: string[]
  is_append: boolean
  role_setting: SystemUserRoleAssignment[]
}

export interface SystemUserPayload {
  id?: string
  username: string
  email: string
  nick_name: string
  password?: string
  phone: string
  role_setting: SystemUserRoleAssignment[]
  encrypted?: boolean
  user_group_ids?: string[]
}

export interface SystemUserUpdateRequest {
  email?: string
  nick_name?: string
  phone?: string
  is_active?: boolean
  role_setting?: SystemUserRoleAssignment[]
  user_group_ids?: string[]
}

/** 系统用户列表项，getUserManagePage 返回的用户记录。 */
export interface SystemUser {
  id: string
  username: string
  nick_name: string
  email: string
  phone: string
  is_active: boolean
  role: string
  source: string
  role_name?: string[]
  role_workspace?: Record<string, string[]>
  role_setting?: SystemUserRoleAssignment[]
  user_group_names?: string[]
  user_group_ids?: string[]
  create_time: string
  update_time?: string
}

export interface SystemUserOption {
  id: string
  nick_name: string
  username: string
}
