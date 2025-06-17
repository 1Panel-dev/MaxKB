interface ChatUserItem {
  create_time: string,
  email: string,
  id: string,
  nick_name: string,
  phone: string,
  source: string,
  update_time: string,
  username: string,
  is_active: boolean,
  user_group_ids?: string[],
  user_group_names?: string[],
}

// TODO
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
export type { ChatUserGroupUserItem, ChatUserItem }