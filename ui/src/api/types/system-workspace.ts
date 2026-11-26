import type { RoleInfo } from './system-role'

/** 系统用户 API 与系统管理工作空间共用的业务类型。 */
export interface WorkspaceItem {
  name: string
  id?: string
  user_count?: number
  /** 当前用户在工作空间中的角色元数据，用于按内置角色 ID 展示当前语言名称。 */
  role_info?: RoleInfo[]
  /** 当前用户在工作空间中的角色名称；普通工作空间列表可能不返回。 */
  role_name?: string[]
}

export interface CreateWorkspaceMemberPayload {
  user_ids: string[]
  role_ids: string[]
}

export interface WorkspaceMemberItem {
  user_relation_id: string
  user_id: string
  username: string
  nick_name: string
  role_id: string
  role_name: string
}
