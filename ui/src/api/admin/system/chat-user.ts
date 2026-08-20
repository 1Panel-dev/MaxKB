import { del, get, post, put } from '../core/request'
import type { ParamsPage, ResponsePage, PasswordRequest } from '../core/types'
import type {
  BatchSetChatUserGroupsRequest,
  ChatUserBase,
  ChatUser,
  ChatUserPayload,
  ChatUserSyncResult,
  ChatUserUpdateRequest,
  RequestParams,
} from '@/api/types'

const prefix = '/system/chat_user'

/** 获取对话用户。 */
const getChatUser = () => {
  return get<ChatUserBase[]>(`${prefix}/list`)
}

/** 获取对话用户分页列表。 */
const getChatUserPage = (page: ParamsPage, query?: RequestParams) => {
  return get<ResponsePage<ChatUser>>(
    `${prefix}/user_manage/${page.currentPage}/${page.pageSize}`,
    query,
  )
}

/** 创建对话用户。 */
const postChatUser = (payload: ChatUserPayload) => {
  return post<ChatUserPayload, ChatUser>(prefix, payload)
}

/** 编辑对话用户。 */
const putChatUser = (userId: string, payload: ChatUserUpdateRequest) => {
  return put<ChatUserUpdateRequest, ChatUser>(`${prefix}/${userId}`, payload)
}

/** 修改对话用户密码。 */
const putChatUserPassword = (userId: string, password: PasswordRequest) => {
  return put<PasswordRequest, boolean>(`${prefix}/${userId}/re_password`, password)
}

/** 删除对话用户。 */
const deleteChatUser = (userId: string) => {
  return del<boolean>(`${prefix}/${userId}`)
}

/** 批量删除对话用户。 */
const postBatchDeleteChatUsers = (userIds: string[]) => {
  return post<string[], boolean>(`${prefix}/batch_delete`, userIds)
}

/** 批量设置对话用户所属用户组。 */
const postBatchSetChatUserGroups = (request: BatchSetChatUserGroupsRequest) => {
  return post<BatchSetChatUserGroupsRequest, boolean>(`${prefix}/batch_add_group`, request)
}

/** 获取可导入的对话用户来源。 */
const getChatUserSyncTypes = () => {
  return get<string[]>(`${prefix}/sync/types`)
}

/** 从指定来源导入对话用户。 */
const postSyncChatUsers = (syncType: string) => {
  return post<undefined, ChatUserSyncResult>(`${prefix}/sync/${syncType}`)
}

export default {
  deleteChatUser,
  getChatUserPage,
  getChatUser,
  getChatUserSyncTypes,
  postBatchDeleteChatUsers,
  postBatchSetChatUserGroups,
  postChatUser,
  postSyncChatUsers,
  putChatUser,
  putChatUserPassword,
}
