interface WorkspaceItem {
  name: string,
  id?: string,
  user_count?: number,
}

interface CreateWorkspaceMemberParamsItem {
  user_ids: string[],
  role_ids: string[]
}

interface WorkspaceMemberItem {
  user_relation_id: string,
  user_id: string,
  username: string,
  nick_name: string,
  role_id: string,
  role_name: string,
}
export type { WorkspaceItem, CreateWorkspaceMemberParamsItem, WorkspaceMemberItem }
