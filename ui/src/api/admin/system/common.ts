import type { CommonUserOption, Dict, SystemUserOption } from '@/api/types'
import { get } from '../core/request'
import { localizeRoleInfo } from '../role-display'

/** 获取默认密码。 */
const getDefaultPassword = () => {
  return get<{ password: string }>(`/user_manage/password`)
}

/** 获得全部用户 */
const getAllUsers = (query?: Dict<unknown>) => {
  return get<SystemUserOption[]>('/user/list', query)
}

/** 获取指定工作空间的普通用户选项。 */
const getWorkspaceMembers = (workspaceId: string, query?: Dict<unknown>) => {
  return get<CommonUserOption[]>(`/workspace/${workspaceId}/user_member`, query).then((users) =>
    users.map((user) => {
      const roleInfo = localizeRoleInfo(user.role_info)
      return roleInfo
        ? {
            ...user,
            role_info: roleInfo,
            roles: roleInfo.map(({ role_name }) => role_name),
          }
        : user
    }),
  )
}

export default { getDefaultPassword, getAllUsers, getWorkspaceMembers }
