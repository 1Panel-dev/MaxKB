
import { SourceTypeEnum } from '@/enums/common'

interface ChatUserGroupItem {
  id: string,
  name: string,
  is_auth: boolean
}

interface ChatUserGroupUserItem {
  id: string,
  is_auth: boolean,
  email: string,
  phone: string,
  nick_name: string,
  username: string,
  password: string,
  source: string,
  is_active: boolean,
  create_time: string,
  update_time: string,
}

interface putUserGroupUserParams {
  chat_user_id: string,
  is_auth: boolean
}
export type { ChatUserGroupItem, putUserGroupUserParams, ChatUserGroupUserItem }
