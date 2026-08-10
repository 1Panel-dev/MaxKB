import { del, get, post, put } from '../core/request'
import type { ParamsPage, ResponsePage, PasswordRequest } from '../core/types'
import type {
  BatchSetChatUserGroupsRequest,
  ChatUserBase,
  ChatUser,
  ChatUserRequest,
  ChatUserUpdateRequest,
  RequestParams,
} from '@/api/types'

const prefix = '/system/chat_user'

/** 获取对话用户。 */
function getChatUser() {
  return get<ChatUserBase[]>(`${prefix}/list`)
}

/** 获取对话用户分页列表。 */
function getChatUserPage(page: ParamsPage, query?: RequestParams) {
  return get<ResponsePage<ChatUser>>(
    `${prefix}/user_manage/${page.currentPage}/${page.pageSize}`,
    query,
  )
}

/** 创建对话用户。 */
function postChatUser(user: ChatUserRequest) {
  return post<ChatUserRequest, ChatUser>(prefix, user)
}

/** 编辑对话用户。 */
function putChatUser(userId: string, user: ChatUserUpdateRequest) {
  return put<ChatUserUpdateRequest, ChatUser>(`${prefix}/${userId}`, user)
}

/** 修改对话用户密码。 */
function putChatUserPassword(userId: string, password: PasswordRequest) {
  return put<PasswordRequest, boolean>(`${prefix}/${userId}/re_password`, password)
}

/** 删除对话用户。 */
function deleteChatUser(userId: string) {
  return del<boolean>(`${prefix}/${userId}`)
}

/** 批量删除对话用户。 */
function postBatchDeleteChatUsers(userIds: string[]) {
  return post<string[], boolean>(`${prefix}/batch_delete`, userIds)
}

/** 批量设置对话用户所属用户组。 */
function postBatchSetChatUserGroups(request: BatchSetChatUserGroupsRequest) {
  return post<BatchSetChatUserGroupsRequest, boolean>(`${prefix}/batch_add_group`, request)
}

export default {
  deleteChatUser,
  getChatUserPage,
  getChatUser,
  postBatchDeleteChatUsers,
  postBatchSetChatUserGroups,
  postChatUser,
  putChatUser,
  putChatUserPassword,
}
