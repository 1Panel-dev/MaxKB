/** 对话用户组 API 与管理页面共用的业务类型。 */

import type { ChatUserBase } from './chat-user'

export interface ChatUserGroupMember extends ChatUserBase {
  user_group_relation_id: string
}

export type ChatGroupMemberOption = ChatUserBase

export interface ChatUserGroupRequest {
  id?: string
  name: string
}
