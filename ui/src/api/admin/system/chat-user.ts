import { get } from '../core/request'
import type { ChatGroupMemberOption } from '@/api/types'

const prefix = '/system/chat_user'

/** 获取对话用户。 */
export function getChatUser() {
  return get<ChatGroupMemberOption[]>(prefix)
}

export default {
  getChatUser,
}
