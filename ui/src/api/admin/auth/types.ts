/** 定义 Admin 登录认证接口使用的数据类型。 */

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
