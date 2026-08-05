/** 普通登录接口、登录配置和登录页面交互使用的数据类型。 */

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

export interface LoginConfig {
  default_value: LoginMethod
  login_methods?: LoginMethod[]
  max_attempts: number
}

export type LoginMode = 'account' | 'qr-code'

export type QrCodeProvider = Extract<LoginMethod, 'dingtalk' | 'lark' | 'wecom'>

export interface AccountLoginForm {
  captcha: string
  password: string
  username: string
}

export interface ForgotPasswordForm {
  email: string
  verificationCode: string
}

export interface LoginOption<T extends string> {
  label: string
  value: T
}
