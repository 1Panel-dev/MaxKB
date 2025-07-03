import { Result } from '@/request/Result'
import { get, post } from '@/request/index'
import type { User, ResetPasswordRequest, CheckCodeRequest } from '@/api/type/user'
import type { Ref } from 'vue'
/**
 * 获取用户基本信息
 * @param loading 接口加载器
 * @returns 用户基本信息
 */
const getUserProfile: (loading?: Ref<boolean>) => Promise<Result<User>> = (loading) => {
  return get('/user/profile', undefined, loading)
}

/**
 * 获取profile
 */
const getProfile: (loading?: Ref<boolean>) => Promise<Result<any>> = (loading) => {
  return get('/profile', undefined, loading)
}
/**
 * 获取全部用户
 */
const getUserList: (loading?: Ref<boolean>) => Promise<Result<Record<string, any>[]>> = (
  loading,
) => {
  return get('/user/list', undefined, loading)
}

/**
 * 获取全部用户
 */
const getAllMemberList: (arg: string, loading?: Ref<boolean>) => Promise<Result<Record<string, any>[]>> = (
  arg,
  loading,
) => {
  return get('/user/list', undefined, loading)
}

/**
 * 校验验证码
 * @param request 请求对象
 * @param loading 接口加载器
 * @returns
 */
const checkCode: (request: CheckCodeRequest, loading?: Ref<boolean>) => Promise<Result<boolean>> = (
  request,
  loading,
) => {
  return post('/user/check_code', request, undefined, loading)
}

/**
 * 发送邮件
 * @param email  邮件地址
 * @param loading 接口加载器
 * @returns
 */
const sendEmit: (
  email: string,
  type: 'register' | 'reset_password',
  loading?: Ref<boolean>,
) => Promise<Result<boolean>> = (email, type, loading) => {
  return post('/user/send_email', { email, type }, undefined, loading)
}

/**
 * 重置密码
 * @param request 重置密码请求参数
 * @param loading 接口加载器
 * @returns
 */
const postResetPassword: (
  request: ResetPasswordRequest,
  loading?: Ref<boolean>,
) => Promise<Result<boolean>> = (request, loading) => {
  return post('/user/re_password', request, undefined, loading)
}

/**
 * 重置密码
 * @param request 重置密码请求参数
 * @param loading 接口加载器
 * @returns
 */
const resetCurrentPassword: (
  request: ResetPasswordRequest,
  loading?: Ref<boolean>,
) => Promise<Result<boolean>> = (request, loading) => {
  return post('/user/current/reset_password', request, undefined, loading)
}

export default {
  getUserProfile,
  getProfile,
  getUserList,
  getAllMemberList,
  postResetPassword,
  checkCode,
  sendEmit,
  resetCurrentPassword,
}
