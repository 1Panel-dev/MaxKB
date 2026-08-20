/** 对话用户 API 与管理页面共用的业务类型。 */

export interface ChatUserBase {
  id: string
  username: string
  nick_name: string
  email: string | null
  phone: string | null
  is_active: boolean
  source: string
  create_time: string
  update_time?: string
}

export interface ChatUser extends ChatUserBase {
  user_group_ids: string[]
  user_group_names: string[]
}

export interface ChatUserPayload {
  username: string
  nick_name: string
  email: string
  phone: string
  user_group_ids: string[]
  password?: string
  encrypted?: boolean
  is_active?: boolean
}

export interface ChatUserUpdateRequest {
  email?: string
  nick_name?: string
  phone?: string
  user_group_ids?: string[]
  is_active?: boolean
}

export interface BatchSetChatUserGroupsRequest {
  ids: string[]
  user_group_ids: string[]
  is_append: boolean
}

export interface ChatUserSyncConflict {
  type: string
  users: string[]
}

export interface ChatUserSyncResult {
  success_count: number
  conflict_users: ChatUserSyncConflict[]
}
