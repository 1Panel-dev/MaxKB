interface User {
  /**
   * 用戶id
   */
  id: string
  /**
   * 用戶名
   */
  username: string
  /**
   * 郵箱
   */
  email: string
  /**
   * 用戶角色
   */
  role: string
  /**
   * 用戶權限
   */
  permissions: Array<string>
  /**
   * 是否需要修改密碼
   */
  is_edit_password?: boolean
}

interface LoginRequest {
  /**
   * 用戶名
   */
  username: string
  /**
   * 密碼
   */
  password: string
}

interface RegisterRequest {
  /**
   * 用戶名
   */
  username: string
  /**
   * 密碼
   */
  password: string
  /**
   * 確定密碼
   */
  re_password: string
  /**
   * 郵箱
   */
  email: string
  /**
   * 驗證碼
   */
  code: string
}

interface CheckCodeRequest {
  /**
   * 郵箱
   */
  email: string
  /**
   *驗證碼
   */
  code: string
  /**
   * 類型
   */
  type: 'register' | 'reset_password'
}

interface ResetCurrentUserPasswordRequest {
  /**
   * 驗證碼
   */
  code: string
  /**
   *密碼
   */
  password: string
  /**
   * 確認密碼
   */
  re_password: string
}

interface ResetPasswordRequest {
  /**
   * 郵箱
   */
  email?: string
  /**
   * 驗證碼
   */
  code?: string
  /**
   * 密碼
   */
  password: string
  /**
   * 確認密碼
   */
  re_password: string
}

export type {
  LoginRequest,
  RegisterRequest,
  CheckCodeRequest,
  ResetPasswordRequest,
  User,
  ResetCurrentUserPasswordRequest
}
