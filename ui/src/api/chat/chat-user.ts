/** 提供当前对话用户档案、密码与 API Key 接口。 */

import { get, post } from './core/request'
import type { ChatUserProfile, ChatUserApiKey } from '@/api/types'

/** 获取当前登录的对话用户档案。 */
const getChatUserProfile = () => {
  return get<ChatUserProfile>('/v3/chat_user/profile')
}

/** 修改当前用户密码，提交 RSA 加密后的表单。 */
const postResetPassword = (data: { encryptedData: string }) => post<{ encryptedData: string }, boolean>('/v3/chat_user/current/reset_password', data)

/** 获取当前用户 API Key；首次读取由服务端创建。 */
const getApiKey = () => get<ChatUserApiKey>('/v3/api_key')

/** 重新生成当前用户 API Key，旧 Key 立即失效。 */
const postApiKey = () => post<undefined, ChatUserApiKey>('/v3/api_key')

export default { getChatUserProfile, postResetPassword, getApiKey, postApiKey }
