import { get } from '../core/request'
import type { RequestParams, SystemUserOption } from '@/api/types'

/** 获取默认密码。 */
const getDefaultPassword = () => {
  return get<{ password: string }>(`/user_manage/password`)
}

/** 获得全部用户 */
const getAllUsers = (query?: RequestParams) => {
  return get<SystemUserOption[]>('/user/list', query)
}

export default {
  getDefaultPassword,
  getAllUsers,
}
