import { get, post, put } from '../../core/request'
import type { AuthProviderSettingPayload, AuthProviderType, OptionItem } from '@/api/types'

const prefix = '/chat_user/auth'

/** 获取对话用户可用的登录方式。 */
const getChatUserAuthType = () => get<OptionItem<string>[]>(`${prefix}/types`)

/** 获取对话用户指定认证源配置。 */
const getAuthSetting = (authType: AuthProviderType) => {
  return get<Partial<AuthProviderSettingPayload>>(`${prefix}/${authType}/detail`)
}

/** 测试对话用户认证源连接。 */
const postAuthSettingConnection = (payload: AuthProviderSettingPayload) => {
  return post<AuthProviderSettingPayload, boolean>(`${prefix}/connection`, payload)
}

/** 保存对话用户指定认证源配置。 */
const putAuthSetting = (authType: AuthProviderType, payload: AuthProviderSettingPayload) => {
  return put<AuthProviderSettingPayload, boolean>(`${prefix}/${authType}/info`, payload)
}
export default { getChatUserAuthType, getAuthSetting, postAuthSettingConnection, putAuthSetting }
