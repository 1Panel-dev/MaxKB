/** 提供单应用对话与门户的认证前置配置、匿名认证、登录和登出接口。 */

import { get, post, promise, request } from './core/request'
import type { ApiResponse } from './core/types'
import type { ApplicationAuthProfile, ChatLoginRequest, ChatLoginResponse, PortalAuthProfile } from '@/api/types'

interface ChatCaptchaResponse {
  captcha: string
}

/** 获取应用的认证前置配置。 */
const getApplicationAuthProfile = (accessToken: string) => {
  return get<ApplicationAuthProfile>('/v3/profile', { access_token: accessToken })
}

/** 获取门户的认证前置配置。 */
const getPortalAuthProfile = () => {
  return get<PortalAuthProfile>('/v3/portal/profile')
}

/** 认证接口携带指定场景本地保存的 token；没有时不附带当前场景的 token。 */
const getSavedTokenHeaders = (savedToken?: string) => ({ Authorization: savedToken ? `Bearer ${savedToken}` : false })

/**
 * 获取匿名访问 token；传入 accessToken 时颁发应用 token，否则颁发门户 token。
 * 携带本地保存的 token 时，后端沿用其中的对话用户，保留历史对话。
 */
const postAnonymousAuth = (accessToken?: string, savedToken?: string) => {
  return promise<string>(
    request.post<ApiResponse<string>>('/v3/auth/anonymous', accessToken ? { access_token: accessToken } : {}, {
      headers: getSavedTokenHeaders(savedToken),
    }),
  )
}

/** 使用对话用户账号登录；传入 accessToken 时登录到对应应用，否则登录门户。携带本地保存的 token。 */
const postLogin = (loginRequest: ChatLoginRequest, accessToken?: string, savedToken?: string) => {
  return promise<ChatLoginResponse>(
    request.post<ApiResponse<ChatLoginResponse>>('/v3/auth/login', loginRequest, {
      params: accessToken ? { accessToken } : undefined,
      headers: getSavedTokenHeaders(savedToken),
    }),
  )
}

/**
 * 获取应用登录验证码；无需验证码时返回空字符串。
 * 后端当前以 `application_id` 查询参数接收 accessToken，且仅支持应用场景。
 */
const getCaptcha = (username: string, accessToken: string) => {
  return get<ChatCaptchaResponse>('/v3/captcha', { username, application_id: accessToken })
}

/** 退出当前对话用户登录状态。 */
const postLogout = () => {
  return post<undefined, boolean>('/v3/auth/logout')
}

export default { getApplicationAuthProfile, getPortalAuthProfile, postAnonymousAuth, postLogin, getCaptcha, postLogout }
