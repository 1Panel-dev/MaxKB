interface LoginRequest {
  /**
   * 用户名
   */
  username: string
  /**
   * 密码
   */
  password: string
  /**
   * 验证码
   */
  captcha: string
  /**
   * 加密数据
   */
  encryptedData?: string
}
export type { LoginRequest }
