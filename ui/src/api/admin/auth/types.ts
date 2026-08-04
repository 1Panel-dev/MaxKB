/** 定义 Admin 登录认证接口使用的数据类型。 */

export interface LoginRequest {
  username: string
  password: string
  captcha?: string
  encryptedData?: string
}

export type LoginMethod =
  | 'CAS'
  | 'LDAP'
  | 'LOCAL'
  | 'OAuth2'
  | 'OIDC'
  | 'SAML2'
  | 'dingtalk'
  | 'lark'
  | 'wecom'

export interface LoginResponse {
  token: string
}

export interface CaptchaResponse {
  captcha: string
}

export interface PlatformInfo {
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

export interface WorkspaceSummary {
  id: string
  name: string
}

export interface CurrentUser {
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
  workspace_list?: WorkspaceSummary[]
}

export interface LoginConfig {
  default_value: LoginMethod
  login_methods?: LoginMethod[]
  max_attempts: number
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
