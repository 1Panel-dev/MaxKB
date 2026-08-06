/** 提供 Admin 第三方认证、扫码登录及客户端授权回调接口。 */

import { get } from '../core/request'
import type { ExternalAuthSetting, LoginResponse, QrCodeSource } from './types'

/** 获取外部认证方式的跳转配置。 */
export function getExternalAuthSetting(authType: string) {
  return get<ExternalAuthSetting>(`/login/auth/${authType}/detail`)
}

/** 获取扫码登录提供商配置。 */
export function getQrCodeSources() {
  return get<QrCodeSource[]>('/qr_type/source')
}

/** 发起 SAML2 登录并返回身份提供方地址。 */
export function getSamlLoginUrl() {
  return get<string>('/saml2')
}

/** 使用钉钉扫码授权码登录。 */
export function getDingTalkCallback(code: string) {
  return get<LoginResponse>('/dingtalk', { code })
}

/** 使用钉钉客户端授权码登录。 */
export function getDingTalkOauthCallback(code: string) {
  return get<LoginResponse>('/dingtalk/oauth2', { code })
}

/** 使用飞书客户端授权码登录。 */
export function getLarkOauthCallback(code: string) {
  return get<LoginResponse>('/lark/oauth2', { code })
}

export default {
  getDingTalkCallback,
  getDingTalkOauthCallback,
  getExternalAuthSetting,
  getLarkOauthCallback,
  getQrCodeSources,
  getSamlLoginUrl,
}
