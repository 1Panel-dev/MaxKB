import { get } from '../../core/request'
import type { ParamsPage, ResponsePage } from '../../core/types'
import type { ChatUserAuthorization, ChatUserAuthorizationGroup, ChatUserAuthorizationResource, Dict } from '@/api/types'
import { getWorkspaceId } from '@/utils/resource-context'

// TODO：V3 联调确认共享授权路径；当前沿用 V2 的大写资源类型，已核对 KNOWLEDGE 查询。
const getPrefix = (resource: ChatUserAuthorizationResource) =>
  `/system/shared/workspace/${getWorkspaceId()}/${resource.resource_type}/${resource.resource_id}`

/** 查询工作空间共享资源的用户组授权状态。 */
const getUserGroupList = (resource: ChatUserAuthorizationResource) => get<ChatUserAuthorizationGroup[]>(`${getPrefix(resource)}/user_group`)

/** 分页查询共享资源的组内用户授权；共享范围不提供写接口。 */
const getUserGroupUserList = (resource: ChatUserAuthorizationResource, userGroupId: string, page: ParamsPage, query?: Dict<unknown>) =>
  get<ResponsePage<ChatUserAuthorization>>(`${getPrefix(resource)}/user_group_id/${userGroupId}/${page.currentPage}/${page.pageSize}`, query)

export default { getUserGroupList, getUserGroupUserList }
