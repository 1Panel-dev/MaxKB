import { del, get, post } from '../core/request'
import type { ParamsPage, ResponsePage } from '../core/types'
import type { Dict, SystemUserGroup, SystemUserGroupMember } from '@/api/types'

const prefix = (workspaceId: string) => `/system/workspace/${workspaceId}/user_group`

/** 获取指定工作空间的系统用户组列表。 */
const getSystemUserGroups = (workspaceId: string) => {
  return get<SystemUserGroup[]>(prefix(workspaceId))
}

/** 创建或更新指定工作空间的系统用户组。 */
const postSystemUserGroup = (workspaceId: string, group: { id?: string; name: string }) => {
  return post<{ id?: string; name: string }, SystemUserGroup>(prefix(workspaceId), group)
}

/** 删除指定工作空间的系统用户组。 */
const deleteSystemUserGroup = (workspaceId: string, groupId: string) => {
  return del<undefined, boolean>(`${prefix(workspaceId)}/${groupId}`)
}

/** 获取指定系统用户组的成员分页列表。 */
const getSystemUserGroupMembers = (workspaceId: string, groupId: string, page: ParamsPage, query?: Dict<unknown>) => {
  return get<ResponsePage<SystemUserGroupMember>>(`${prefix(workspaceId)}/${groupId}/user_list/${page.currentPage}/${page.pageSize}`, query)
}

/** 向指定系统用户组添加成员。 */
const postSystemUserGroupMembers = (workspaceId: string, groupId: string, userIds: string[]) => {
  return post<{ user_ids: string[] }, boolean>(`${prefix(workspaceId)}/${groupId}/add_member`, { user_ids: userIds })
}

/** 从指定系统用户组移除成员。 */
const postRemoveSystemUserGroupMembers = (workspaceId: string, groupId: string, relationIds: string[]) => {
  return del<{ group_relation_ids: string[] }, boolean>(`${prefix(workspaceId)}/${groupId}/remove_member`, undefined, { group_relation_ids: relationIds })
}

export default { deleteSystemUserGroup, getSystemUserGroupMembers, getSystemUserGroups, postRemoveSystemUserGroupMembers, postSystemUserGroup, postSystemUserGroupMembers }
