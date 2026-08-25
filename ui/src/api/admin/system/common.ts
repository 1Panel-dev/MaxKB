import { get } from '../core/request'
import type { RequestParams, SystemUserOption, CommonUserOption } from '@/api/types'

/** 获取默认密码。 */
const getDefaultPassword = () => {
  return get<{ password: string }>(`/user_manage/password`)
}

/** 获得全部用户 */
const getAllUsers = (query?: RequestParams) => {
  return get<SystemUserOption[]>('/user/list', query)
}

/** 获取指定工作空间的普通用户选项。 */
const getWorkspaceMembers = (workspaceId: string, query?: RequestParams) => {
  return get<CommonUserOption[]>(`/workspace/${workspaceId}/user_member`, query)
}



export default {
  getDefaultPassword,
  getAllUsers,
  getWorkspaceMembers,
}
