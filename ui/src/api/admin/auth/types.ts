/** Admin 认证 API 及其 Store 消费方共同使用的类型。 */

import type { LoginMethod, QrCodeConfig, SelectOption } from '@/types'

export interface CurrentUserInfo {
  email: string
  id: string
  is_edit_password?: boolean
  language?: string
  nick_name: string
  permissions: string[]
  role: string[]
  role_name?: string[]
  source?: string
  username: string
  workspace_list?: SelectOption[]
}

export interface LoginRequest {
  username: string
  password: string
  captcha?: string
  encryptedData?: string
}

export interface LoginResponse {
  token: string
}

export interface CaptchaResponse {
  captcha: string
}

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

export interface QrCodeSource {
  auth_type: Extract<LoginMethod, 'dingtalk' | 'lark' | 'wecom'>
  config: QrCodeConfig
}

export interface BaseProfile {
  edition: 'CE' | 'EE' | 'PE'
  license_is_valid: boolean
  permissions?: string[]
  role?: string[]
  rsa: string
  version?: string
}

export interface ThemeInfo {
  forumUrl?: string
  icon?: string
  loginImage?: string
  loginLogo?: string
  projectUrl?: string
  showForum?: boolean
  showProject?: boolean
  showUserManual?: boolean
  slogan?: string
  theme?: string
  title?: string
  userManualUrl?: string
}
