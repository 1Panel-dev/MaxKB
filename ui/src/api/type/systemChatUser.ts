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

interface ChatUserGroupUserItem {
  id: string,
  email: string,
  phone: string,
  nick_name: string,
  username: string,
  source: string,
  is_active: boolean,
  create_time: string,
  update_time: string,
  user_group_relation_id: string,
}
export type { ChatUserGroupUserItem, ChatUserItem }
