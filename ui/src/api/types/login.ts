/** 登录 API 与登录页面共同使用的业务类型。 */

import { LOGIN_METHOD } from '@/api/enums'

export type LoginMethod = (typeof LOGIN_METHOD)[keyof typeof LOGIN_METHOD]

export interface LoginConfig {
  default_value: LoginMethod
  login_methods?: LoginMethod[]
  max_attempts: number
}

export type QrCodeProvider = Extract<LoginMethod, typeof LOGIN_METHOD.DINGTALK | typeof LOGIN_METHOD.LARK | typeof LOGIN_METHOD.WECOM>

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
