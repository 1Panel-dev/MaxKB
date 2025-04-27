import { Result } from '@/request/Result'
import { get, post } from '@/request/index'
import type { User } from '@/api/type/user'
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
 * 获取版本profile
 */
// const getProfile: (loading?: Ref<boolean>) => Promise<Result<any>> = (loading) => {
//   return get('/profile', undefined, loading)
// }

export default {
  getUserProfile,
}
