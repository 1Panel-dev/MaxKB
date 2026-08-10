/** 提供 Admin 普通账号登录、LDAP 登录、登出和验证码接口。 */

import { get, post } from '../core/request'
import type { CaptchaResponse, LoginRequest, LoginResponse } from './types'

/** 使用账号和密码登录 Admin 应用。 */
function postLogin(loginRequest: LoginRequest) {
  return post<LoginRequest, LoginResponse>('/user/login', loginRequest)
}

/** 使用 LDAP 账号登录 Admin 应用。 */
function postLdapLogin(loginRequest: LoginRequest) {
  return post<LoginRequest, LoginResponse>('/ldap/login', loginRequest)
}

/** 退出当前 Admin 登录状态。 */
function postLogout() {
  return post<boolean>('/user/logout')
}

/** 获取当前账号所需的登录验证码。 */
function getCaptcha(username?: string) {
  return get<CaptchaResponse>('/user/captcha', { username })
}

export default {
  getCaptcha,
  postLdapLogin,
  postLogin,
  postLogout,
}
