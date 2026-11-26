/** 提供 Admin 登录后的当前用户接口。 */

import type { PasswordRequest } from '../core/types'
import type { CurrentUserInfo } from './types'
import type { ListItem } from '@/api/types'
import { get, post } from '../core/request'
import { localizeRoleName, localizeRoleSource } from '../role-display'

/** 获取当前登录用户、权限、语言及可用工作空间。 */
const getCurrentUserInfo = () => {
  return get<CurrentUserInfo>('/user/profile').then((userInfo) => {
    const localizedUserInfo = localizeRoleSource(userInfo)
    if (!userInfo.workspace_list) return localizedUserInfo
    return {
      ...localizedUserInfo,
      workspace_list: userInfo.workspace_list.map(localizeRoleSource),
    }
  })
}

/** 获取当前用户可分配的工作空间列表。 */
const getCurrentUserWorkspaceList = () => {
  return get<ListItem[]>('/workspace/current_user')
}

/** 获取当前用户可分配的角色列表。 */
const getCurrentUserRoleList = (): Promise<ListItem[]> => {
  return get<ListItem[]>('/role_list/current_user').then((roles) =>
    roles.map((role) => ({
      ...role,
      name: localizeRoleName(role.id, role.name),
    })),
  )
}

/** 修改当前登录用户的密码，成功后当前登录凭据失效。 */
const postCurrentUserPassword = (password: PasswordRequest) => {
  return post<PasswordRequest, boolean>('/user/current/reset_password', password)
}

/** 保存当前账号的语言偏好。 */
const postCurrentUserLanguage = (language: string) => {
  return post<{ language: string }, void>('/user/language', { language })
}

export default { postCurrentUserLanguage, postCurrentUserPassword, getCurrentUserInfo, getCurrentUserRoleList, getCurrentUserWorkspaceList }
