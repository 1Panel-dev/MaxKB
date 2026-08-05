/** 提供 Admin 登录后的当前用户接口。 */

import { get } from '../core/request'
import type { CurrentUser } from '@/types'

/** 获取当前登录用户、权限、语言及可用工作空间。 */
export function getCurrentUser() {
  return get<CurrentUser>('/user/profile')
}

export default {
  getCurrentUser,
}
