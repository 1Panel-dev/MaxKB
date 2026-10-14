import { get, put } from '../../core/request'
import type { ParamsPage, ResponsePage } from '../../core/types'
import type {
  ChatUserAuthorization,
  ChatUserAuthorizationGroup,
  ChatUserAuthorizationResource,
  ChatUserGroupAuthorizationPayload,
  ChatUserAuthorizationPayload,
  Dict,
} from '@/api/types'

// TODO：V3 联调确认授权前缀；当前沿用 V2 的 /system/shared/knowledge/{resource_type}。
const getPrefix = (resource: ChatUserAuthorizationResource) => `/system/shared/knowledge/${resource.resource_type}/${resource.resource_id}`

/** 获取资源的对话用户组及自动授权状态。 */
const getUserGroupList = (resource: ChatUserAuthorizationResource) => get<ChatUserAuthorizationGroup[]>(`${getPrefix(resource)}/user_group`)

/** 保存资源的用户组自动授权设置。 */
const putUserGroupAuthorization = (resource: ChatUserAuthorizationResource, data: ChatUserGroupAuthorizationPayload[]) =>
  put<ChatUserGroupAuthorizationPayload[], boolean>(`${getPrefix(resource)}/user_group`, data)

/** 分页查询用户组内的对话用户及资源授权状态。 */
const getUserGroupUserList = (resource: ChatUserAuthorizationResource, userGroupId: string, page: ParamsPage, query?: Dict<unknown>) =>
  get<ResponsePage<ChatUserAuthorization>>(`${getPrefix(resource)}/user_group_id/${userGroupId}/${page.currentPage}/${page.pageSize}`, query)

/** 保存用户组内的对话用户资源授权。 */
const putUserGroupUser = (resource: ChatUserAuthorizationResource, userGroupId: string, data: ChatUserAuthorizationPayload[]) =>
  put<ChatUserAuthorizationPayload[], boolean>(`${getPrefix(resource)}/user_group_id/${userGroupId}`, data)

export default { getUserGroupList, putUserGroupAuthorization, getUserGroupUserList, putUserGroupUser }
