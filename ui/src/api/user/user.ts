import { Result } from '@/request/Result'
import { get, post } from '@/request/index'
import type { User, ResetPasswordRequest } from '@/api/type/user'
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
 * 获取版本profile
 */
// const getProfile: (loading?: Ref<boolean>) => Promise<Result<any>> = (loading) => {
//   return get('/profile', undefined, loading)
// }

/**
 * 获取全部用户
 */
const getUserList: (loading?: Ref<boolean>) => Promise<Result<Record<string, any>[]>> = (
  loading,
) => {
  return get('/user/list', undefined, loading)
}

/**
 * 重置密码
 * @param request 重置密码请求参数
 * @param loading 接口加载器
 * @returns
 */
const resetPassword: (
  request: ResetPasswordRequest,
  loading?: Ref<boolean>,
) => Promise<Result<boolean>> = (request, loading) => {
  return post('/user/re_password', request, undefined, loading)
}

export default {
  getUserProfile,
  getProfile,
  getUserList,
  resetPassword,
}
