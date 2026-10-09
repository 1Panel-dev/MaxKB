/** 提供当前对话用户档案接口。 */

import { get } from './core/request'
import type { ChatUserProfile } from '@/api/types'

/** 获取当前登录的对话用户档案。 */
const getChatUserProfile = () => {
  return get<ChatUserProfile>('/v3/chat_user/profile')
}

export default { getChatUserProfile }
