/** 对话用户组 API 与管理页面共用的业务类型。 */

export interface ChatUserGroupMember {
  id: string
  username: string
  nick_name: string
  email: string
  phone: string
  is_active: boolean
  source: string
  create_time: string
  update_time: string
  user_group_relation_id: string
}

export type ChatGroupMemberOption = Omit<ChatUserGroupMember, 'user_group_relation_id'>

export interface ChatUserGroupRequest {
  id?: string
  name: string
}
