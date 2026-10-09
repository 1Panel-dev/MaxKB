/** Chat 与 Portal 入口共用的认证前置配置、登录与对话用户档案类型。 */

import type { ChatUserTokenQuota } from './chat-user'
import type { LoginMethod } from './login'

/** 认证前置配置，应用与门户共用结构，差异字段放在 `meta`。 */
export interface AuthProfile<Meta = Record<string, never>> {
  max_attempts: number
  enable_auth: boolean
  login_value: LoginMethod[]
  rsa_key: string
  meta: Meta
}

export interface ApplicationAuthProfileMeta {
  application_id: string
  application_name: string
}

/** 单应用对话的认证前置配置。 */
export type ApplicationAuthProfile = AuthProfile<ApplicationAuthProfileMeta>

/** 门户的认证前置配置。 */
export type PortalAuthProfile = AuthProfile

export interface ChatLoginRequest {
  username: string
  password?: string
  captcha?: string
  encryptedData?: string
}

export interface ChatLoginResponse {
  token: string
}

/** 当前登录的对话用户档案。 */
export interface ChatUserProfile {
  id: string
  username: string
  nick_name: string
  email: string
  source: string
  token_quota: Omit<ChatUserTokenQuota, 'period_end'> | null
}
