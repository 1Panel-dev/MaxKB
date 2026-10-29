/** Admin 认证 API 及其 Store 消费方共同使用的类型。 */

import type { WorkspaceItem } from '@/api/types'

export interface CurrentUserInfo {
  email: string
  id: string
  is_edit_password?: boolean
  language?: string
  nick_name: string
  /** 权限位图：key 为「组(+工作空间+资源)」，value 为该组内操作授权位按位或的十六进制字符串（不带 0x 前缀，避免超过 2^53 丢精度）。 */
  permissions: Record<string, string>
  role: string[]
  role_name?: string[]
  source?: string
  username: string
  workspace_list?: WorkspaceItem[]
}

export interface LoginRequest {
  username: string
  password?: string
  captcha?: string
  encryptedData?: string
}

export interface LoginResponse {
  token: string
}

export interface CaptchaResponse {
  captcha: string
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
