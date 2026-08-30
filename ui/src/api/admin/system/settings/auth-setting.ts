import { get, post, put } from '../../core/request'
import type { AuthProviderSettingPayload, AuthProviderType, LoginAuthSettingPayload } from '@/api/types'

const prefix = '/auth'

/** 获取指定认证源配置。 */
const getAuthSetting = (authType: AuthProviderType) => {
  return get<Partial<AuthProviderSettingPayload>>(`${prefix}/${authType}/detail`)
}

/** 测试认证源连接。 */
const postAuthSettingConnection = (payload: AuthProviderSettingPayload) => {
  return post<AuthProviderSettingPayload, boolean>(`${prefix}/connection`, payload)
}

/** 保存指定认证源配置。 */
const putAuthSetting = (authType: AuthProviderType, payload: AuthProviderSettingPayload) => {
  return put<AuthProviderSettingPayload, boolean>(`${prefix}/${authType}/info`, payload)
}

/** 获取系统登录设置。 */
const getLoginSetting = () => {
  return get<LoginAuthSettingPayload>(`${prefix}/setting`)
}

/** 保存系统登录设置。 */
const putLoginSetting = (payload: LoginAuthSettingPayload) => {
  return put<LoginAuthSettingPayload, boolean>(`${prefix}/setting`, payload)
}

export default { getAuthSetting, getLoginSetting, postAuthSettingConnection, putAuthSetting, putLoginSetting }
