export type LoginMode = 'account' | 'qr-code'

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

export type QrCodeProvider = Extract<LoginMethod, 'dingtalk' | 'lark' | 'wecom'>

export interface LoginConfig {
  default_value: LoginMethod
  login_methods: LoginMethod[]
}

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
