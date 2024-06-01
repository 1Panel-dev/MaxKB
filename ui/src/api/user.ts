import { Result } from '@/request/Result'
import { get, post } from '@/request/index'
import type {
  LoginRequest,
  RegisterRequest,
  CheckCodeRequest,
  ResetPasswordRequest,
  User,
  ResetCurrentUserPasswordRequest
} from '@/api/type/user'
import type { Ref } from 'vue'

/**
 * 登錄
 * @param request 登錄接口請求表單
 * @param loading 接口加載器
 * @returns 認證數據
 */
const login: (request: LoginRequest, loading?: Ref<boolean>) => Promise<Result<string>> = (
  request,
  loading
) => {
  return post('/user/login', request, undefined, loading)
}
/**
 * 登出
 * @param loading 接口加載器
 * @returns
 */
const logout: (loading?: Ref<boolean>) => Promise<Result<boolean>> = (loading) => {
  return post('/user/logout', undefined, undefined, loading)
}

/**
 * 註冊用戶
 * @param request 註冊請求對象
 * @param loading 接口加載器
 * @returns
 */
const register: (request: RegisterRequest, loading?: Ref<boolean>) => Promise<Result<string>> = (
  request,
  loading
) => {
  return post('/user/register', request, undefined, loading)
}

/**
 * 校驗驗證碼
 * @param request 請求對象
 * @param loading 接口加載器
 * @returns
 */
const checkCode: (request: CheckCodeRequest, loading?: Ref<boolean>) => Promise<Result<boolean>> = (
  request,
  loading
) => {
  return post('/user/check_code', request, undefined, loading)
}

/**
 * 發送郵件
 * @param email  郵件地址
 * @param loading 接口加載器
 * @returns
 */
const sendEmit: (
  email: string,
  type: 'register' | 'reset_password',
  loading?: Ref<boolean>
) => Promise<Result<boolean>> = (email, type, loading) => {
  return post('/user/send_email', { email, type }, undefined, loading)
}
/**
 * 發送郵件到當前用戶
 * @param loading  發送驗證碼到當前用戶
 * @returns
 */
const sendEmailToCurrent: (loading?: Ref<boolean>) => Promise<Result<boolean>> = (loading) => {
  return post('/user/current/send_email', undefined, undefined, loading)
}
/**
 * 修改當前用戶密碼
 * @param request 請求對象
 * @param loading 加載器
 * @returns
 */
const resetCurrentUserPassword: (
  request: ResetCurrentUserPasswordRequest,
  loading?: Ref<boolean>
) => Promise<Result<boolean>> = (request, loading) => {
  return post('/user/current/reset_password', request, undefined, loading)
}
/**
 * 獲取用戶基本信息
 * @param loading 接口加載器
 * @returns 用戶基本信息
 */
const profile: (loading?: Ref<boolean>) => Promise<Result<User>> = (loading) => {
  return get('/user', undefined, loading)
}

/**
 * 重置密碼
 * @param request 重置密碼請求參數
 * @param loading 接口加載器
 * @returns
 */
const resetPassword: (
  request: ResetPasswordRequest,
  loading?: Ref<boolean>
) => Promise<Result<boolean>> = (request, loading) => {
  return post('/user/re_password', request, undefined, loading)
}

/**
 * 添加團隊需要查詢用戶列表
 * @param loading 接口加載器
 * email_or_username
 */
const getUserList: (email_or_username: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  email_or_username,
  loading
) => {
  return get('/user/list', { email_or_username }, loading)
}

/**
 * 獲取version
 */
const getVersion: (loading?: Ref<boolean>) => Promise<Result<any>> = (loading) => {
  return get('/profile', undefined, loading)
}

export default {
  login,
  register,
  sendEmit,
  checkCode,
  profile,
  resetPassword,
  sendEmailToCurrent,
  resetCurrentUserPassword,
  logout,
  getUserList,
  getVersion
}
