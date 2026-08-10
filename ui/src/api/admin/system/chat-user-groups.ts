import { del, get, post } from '../core/request'
import type { ParamsPage, ResponsePage } from '../core/types'
import type {
  ChatUserGroupMember,
  ChatUserGroupRequest,
  ListItem,
  RequestParams,
} from '@/api/types'

const prefix = '/system/group'

/** 获取全部对话用户组。 */
export function getChatUserGroups() {
  return get<ListItem[]>(prefix)
}

/** 创建或重命名对话用户组。 */
export function postChatUserGroup(group: ChatUserGroupRequest) {
  return post<ChatUserGroupRequest, boolean>(prefix, group)
}

/** 删除对话用户组。 */
export function deleteChatUserGroup(groupId: string) {
  return del<undefined, boolean>(`${prefix}/${groupId}`)
}

/** 获取用户组成员分页列表。 */
export function getChatUserGroupMembers(groupId: string, page: ParamsPage, query?: RequestParams) {
  return get<ResponsePage<ChatUserGroupMember>>(
    `${prefix}/${groupId}/user_list/${page.currentPage}/${page.pageSize}`,
    query,
  )
}

/** 添加对话用户组成员。 */
export function postChatUserGroupMembers(groupId: string, userIds: string[]) {
  return post<{ user_ids: string[] }, boolean>(`${prefix}/${groupId}/add_member`, {
    user_ids: userIds,
  })
}

/** 移除对话用户组成员。 */
export function postRemoveChatUserGroupMembers(groupId: string, relationIds: string[]) {
  return post<{ group_relation_ids: string[] }, boolean>(`${prefix}/${groupId}/remove_member`, {
    group_relation_ids: relationIds,
  })
}

export default {
  deleteChatUserGroup,
  getChatUserGroupMembers,
  getChatUserGroups,
  postChatUserGroup,
  postChatUserGroupMembers,
  postRemoveChatUserGroupMembers,
}
