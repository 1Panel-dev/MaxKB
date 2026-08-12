import { get, post, put } from '../core/request'
import type { AuthProviderSetting, AuthProviderType, LoginAuthSetting } from '@/api/types'

const prefix = '/chat_user/auth'

/** 获取对话用户指定认证源配置。 */
const getAuthSetting = (authType: AuthProviderType) => {
  return get<Partial<AuthProviderSetting>>(`${prefix}/${authType}/detail`)
}

/** 测试对话用户认证源连接。 */
const postAuthSettingConnection = (setting: AuthProviderSetting) => {
  return post<AuthProviderSetting, boolean>(`${prefix}/connection`, setting)
}

/** 保存对话用户指定认证源配置。 */
const putAuthSetting = (authType: AuthProviderType, setting: AuthProviderSetting) => {
  return put<AuthProviderSetting, boolean>(`${prefix}/${authType}/info`, setting)
}

/** 获取对话用户登录设置。 */
const getLoginSetting = () => {
  return get<LoginAuthSetting>(`${prefix}/setting`)
}

/** 保存对话用户登录设置。 */
const putLoginSetting = (setting: LoginAuthSetting) => {
  return put<LoginAuthSetting, boolean>(`${prefix}/setting`, setting)
}

export default {
  getAuthSetting,
  getLoginSetting,
  postAuthSettingConnection,
  putAuthSetting,
  putLoginSetting,
}
