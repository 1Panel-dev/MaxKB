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

/** 系统中选择空间下的成员用户
 * @param workspaceId 工作空间ID
 * 资源授权  和用户组的 用户下拉列表使用
 */
const getWorkspaceMembers = (workspaceId: string, query?: RequestParams) => {
  return get<SystemUserOption[]>(`/workspace/${workspaceId}/user_member`, query)
}

export default {
  getDefaultPassword,
  getAllUsers,
  getWorkspaceMembers,
}
