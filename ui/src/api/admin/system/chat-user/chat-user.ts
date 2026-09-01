import { del, get, post, put } from '../../core/request'
import type { ParamsPage, ResponsePage, PasswordRequest } from '../../core/types'
import type {
  BatchSetChatUserQuotaRequest,
  BatchSetChatUserQuotaResult,
  BatchSetChatUserGroupsRequest,
  ChatUserBase,
  ChatUser,
  ChatUserPayload,
  ChatUserQuota,
  ChatUserQuotaPayload,
  ChatUserSyncResult,
  ChatUserUpdateRequest,
  Dict,
} from '@/api/types'

const prefix = '/system/chat_user'

/** 获取对话用户。 */
const getChatUser = () => {
  return get<ChatUserBase[]>(`${prefix}/list`)
}

/** 获取对话用户分页列表。 */
const getChatUserPage = (page: ParamsPage, query?: Dict<unknown>) => {
  return get<ResponsePage<ChatUser>>(`${prefix}/user_manage/${page.currentPage}/${page.pageSize}`, query)
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

/** 获取对话用户 Token 配额。 */
const getChatUserQuota = (userId: string) => {
  return get<ChatUserQuota>(`${prefix}/${userId}/quota`)
}

/** 设置对话用户 Token 配额。 */
const postChatUserQuota = (userId: string, payload: ChatUserQuotaPayload) => {
  return post<ChatUserQuotaPayload, ChatUserQuota>(`${prefix}/${userId}/quota`, payload)
}

/** 批量设置对话用户 Token 配额。 */
const postBatchSetChatUserQuota = (request: BatchSetChatUserQuotaRequest) => {
  return post<BatchSetChatUserQuotaRequest, BatchSetChatUserQuotaResult>(`${prefix}/batch_quota`, request)
}

/** 获取可导入的对话用户来源。 */
const getChatUserSyncTypes = () => {
  return get<string[]>(`${prefix}/sync/types`)
}

/** 从指定来源导入对话用户（file 来源需携带 xlsx 文件）。 */
const postSyncChatUsers = (syncType: string, defaultGroupId?: string, syncFile?: File) => {
  if (syncFile) {
    const payload = new FormData()
    payload.append('xlsx_file', syncFile)
    if (defaultGroupId) payload.append('default_group_id', defaultGroupId)
    return post<FormData, ChatUserSyncResult>(`${prefix}/sync/${syncType}`, payload)
  }
  return post<{ default_group_id?: string }, ChatUserSyncResult>(`${prefix}/sync/${syncType}`, { default_group_id: defaultGroupId })
}

export default {
  deleteChatUser,
  getChatUserQuota,
  getChatUserPage,
  getChatUser,
  getChatUserSyncTypes,
  postBatchDeleteChatUsers,
  postBatchSetChatUserGroups,
  postBatchSetChatUserQuota,
  postChatUser,
  postChatUserQuota,
  postSyncChatUsers,
  putChatUser,
  putChatUserPassword,
}
