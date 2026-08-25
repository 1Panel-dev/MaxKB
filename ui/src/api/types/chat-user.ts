/** 对话用户 API 与管理页面共用的业务类型。 */

import { PERIOD_TYPE, QUOTA_TYPE } from '@/api/enums'

export interface ChatUserBase {
  id: string
  username: string
  nick_name: string
  email: string | null
  phone: string | null
  is_active: boolean
  source: string
  create_time: string
  update_time?: string
}

export interface ChatUser extends ChatUserBase {
  user_group_ids: string[]
  user_group_names: string[]
  token_quota?: ChatUserTokenQuota | null
}

export interface ChatUserPayload {
  username: string
  nick_name: string
  email: string
  phone: string
  user_group_ids: string[]
  password?: string
  encrypted?: boolean
  is_active?: boolean
}

export interface ChatUserUpdateRequest {
  email?: string
  nick_name?: string
  phone?: string
  user_group_ids?: string[]
  is_active?: boolean
}

export interface BatchSetChatUserGroupsRequest {
  ids: string[]
  user_group_ids: string[]
  is_append: boolean
}

export interface ChatUserSyncConflict {
  type: string
  users: string[]
}

export interface ChatUserSyncResult {
  success_count: number
  conflict_users: ChatUserSyncConflict[]
}

/** 对话用户列表中的 Token 配额概要（由列表接口按用户合并返回）。 */
export interface ChatUserTokenQuota {
  quota_type: QuotaType
  used_tokens: number
  token_limit: number | null
  total_tokens: number
  period_end: string | null
}

/** 对话用户 Token 配额类型。 */
export type QuotaType = (typeof QUOTA_TYPE)[keyof typeof QUOTA_TYPE]
export type PeriodType = (typeof PERIOD_TYPE)[keyof typeof PERIOD_TYPE]

/** 对话用户 Token 配额。 */
export interface ChatUserQuota {
  user_id: string
  quota_type: QuotaType
  quota_type_label: string
  period_type?: PeriodType | null
  period_type_label?: string | null
  period_value?: number | null
  token_limit?: number | null
  used_tokens?: number
  total_tokens?: number
  period_end?: string | null
}

/** 设置对话用户 Token 配额请求体。 */
export interface ChatUserQuotaPayload {
  quota_type: QuotaType
  period_type: PeriodType | null
  period_value: number | null
  token_limit: number | null
}

/** 批量设置对话用户 Token 配额请求体。 */
export interface BatchSetChatUserQuotaRequest extends ChatUserQuotaPayload {
  user_ids: string[]
}

/** 批量设置对话用户 Token 配额结果。 */
export interface BatchSetChatUserQuotaResult {
  success_count: number
  failed_count: number
}
