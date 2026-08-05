/** 第三方登录和扫码登录使用的数据类型。 */

import type { LoginMethod } from './login'

export interface ExternalAuthConfig {
  authEndpoint?: string
  clientId?: string
  ldpUri?: string
  redirectUrl: string
  scope?: string
  state?: string
}

export interface ExternalAuthSetting {
  config?: ExternalAuthConfig
}

export interface QrCodeConfig {
  agent_id?: string
  app_key: string
  app_secret: string
  callback_url?: string
  corp_id?: string
  qr_url?: string
}

export interface QrCodeSource {
  auth_type: Extract<LoginMethod, 'dingtalk' | 'lark' | 'wecom'>
  config: QrCodeConfig
}
