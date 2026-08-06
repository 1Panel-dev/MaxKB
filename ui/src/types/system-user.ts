/** 系统用户管理使用的数据类型。 */

export interface SystemUserQuery extends Record<string, unknown> {
  email?: string
  is_active?: boolean
  nick_name?: string
  source?: string
  username?: string
}

export interface SystemUser {
  create_time: string
  email: string
  id: string
  is_active: boolean
  nick_name: string
  phone: string | null
  role: string
  role_name?: string[]
  role_setting?: Array<{
    role_id: string
    workspace_ids: string[]
  }>
  role_workspace?: Record<string, string[]>
  source: string
  update_time: string
  user_group_ids: string[]
  user_group_names: string[]
  user_group_workspace: unknown[]
  username: string
}
