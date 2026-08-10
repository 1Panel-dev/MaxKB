/** 登录 API 与登录页面共同使用的业务类型。 */

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

export interface LoginConfig {
  default_value: LoginMethod
  login_methods?: LoginMethod[]
  max_attempts: number
}

export type QrCodeProvider = Extract<LoginMethod, 'dingtalk' | 'lark' | 'wecom'>

export interface QrCodeConfig {
  agent_id?: string
  app_key: string
  app_secret: string
  callback_url?: string
  corp_id?: string
  qr_url?: string
}

export interface UpdatePasswordForm {
  password: string
  re_password: string
}
