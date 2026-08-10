/** 提供 Admin 登录后的当前用户接口。 */

import { get } from '../core/request'
import type { ListItem } from '@/api/types'
import type { CurrentUserInfo } from './types'

/** 获取当前登录用户、权限、语言及可用工作空间。 */
export function getCurrentUserInfo() {
  return get<CurrentUserInfo>('/user/profile')
}

/** 获取当前用户可分配的工作空间列表。 */
export function getCurrentUserWorkspaceList() {
  return get<ListItem[]>('/workspace/current_user')
}

/** 获取当前用户可分配的角色列表。 */
export function getCurrentUserRoleList() {
  return get<ListItem[]>('/role_list/current_user')
}

export default {
  getCurrentUserInfo,
  getCurrentUserRoleList,
  getCurrentUserWorkspaceList,
}
