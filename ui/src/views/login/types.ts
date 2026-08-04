import type { LoginConfig, LoginMethod } from '@/api/admin/auth/types'

export type { LoginConfig, LoginMethod }

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
