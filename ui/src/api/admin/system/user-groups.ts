import { del, get, post } from '../core/request'
import type { ParamsPage, ResponsePage } from '../core/types'
import type { ListItem, RequestParams } from '@/api/types'

export interface SystemUserGroup {
  id: string
  name: string
  workspace_id: string
  count: number
}

export interface SystemUserGroupMember {
  id: string
  username: string
  email: string
  phone: string
  is_active: boolean
  role: string
  nick_name: string
  create_time: string
  update_time: string
  source: string
  system_user_group_relation_id: string
}

const prefix = (workspaceId: string) => `/system/workspace/${workspaceId}/user_group`

const getSystemUserGroups = (workspaceId: string) => {
  return get<SystemUserGroup[]>(prefix(workspaceId))
}

const postSystemUserGroup = (workspaceId: string, group: { id?: string; name: string }) => {
  return post<{ id?: string; name: string }, SystemUserGroup>(prefix(workspaceId), group)
}

const deleteSystemUserGroup = (workspaceId: string, groupId: string) => {
  return del<undefined, boolean>(`${prefix(workspaceId)}/${groupId}`)
}

const getSystemUserGroupMembers = (
  workspaceId: string,
  groupId: string,
  page: ParamsPage,
  query?: RequestParams,
) => {
  return get<ResponsePage<SystemUserGroupMember>>(
    `${prefix(workspaceId)}/${groupId}/user_list/${page.currentPage}/${page.pageSize}`,
    query,
  )
}

const postSystemUserGroupMembers = (workspaceId: string, groupId: string, userIds: string[]) => {
  return post<{ user_ids: string[] }, boolean>(`${prefix(workspaceId)}/${groupId}/add_member`, {
    user_ids: userIds,
  })
}

const postRemoveSystemUserGroupMembers = (
  workspaceId: string,
  groupId: string,
  relationIds: string[],
) => {
  return del<{ group_relation_ids: string[] }, boolean>(
    `${prefix(workspaceId)}/${groupId}/remove_member`,
    undefined,
    { group_relation_ids: relationIds },
  )
}

export default {
  deleteSystemUserGroup,
  getSystemUserGroupMembers,
  getSystemUserGroups,
  postRemoveSystemUserGroupMembers,
  postSystemUserGroup,
  postSystemUserGroupMembers,
}
