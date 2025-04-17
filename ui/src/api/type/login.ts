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
  code: string
}
export type { LoginRequest }
