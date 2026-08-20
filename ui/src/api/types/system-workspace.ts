/** 系统用户 API 与系统管理工作空间共用的业务类型。 */
export interface WorkspaceItem {
  name: string
  id?: string
  user_count?: number
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
