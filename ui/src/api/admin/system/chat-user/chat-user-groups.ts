import { del, get, post } from '../../core/request'
import type { ParamsPage, ResponsePage } from '../../core/types'
import type { ChatUserGroupMember, ChatUserGroupPayload, ListItem, Dict } from '@/api/types'

const prefix = '/system/group'

/** 获取全部对话用户组。 */
const getChatUserGroups = () => {
  return get<ListItem[]>(prefix)
}

/** 创建或重命名对话用户组。 */
const postChatUserGroup = (payload: ChatUserGroupPayload) => {
  return post<ChatUserGroupPayload, boolean>(prefix, payload)
}

/** 删除对话用户组。 */
const deleteChatUserGroup = (groupId: string) => {
  return del<undefined, boolean>(`${prefix}/${groupId}`)
}

/** 获取用户组成员分页列表。 */
const getChatUserGroupMembers = (groupId: string, page: ParamsPage, query?: Dict<unknown>) => {
  return get<ResponsePage<ChatUserGroupMember>>(
    `${prefix}/${groupId}/user_list/${page.currentPage}/${page.pageSize}`,
    query,
  )
}

/** 添加对话用户组成员。 */
const postChatUserGroupMembers = (groupId: string, userIds: string[]) => {
  return post<{ user_ids: string[] }, boolean>(`${prefix}/${groupId}/add_member`, {
    user_ids: userIds,
  })
}

/** 移除对话用户组成员。 */
const postRemoveChatUserGroupMembers = (groupId: string, relationIds: string[]) => {
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
