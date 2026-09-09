import { get, put } from '../core/request'
import type { ParamsPage, ResponsePage } from '../core/types'
import type { Dict, ResourceAuthorizationTargetType, ResourceUserPermission, ResourceUserPermissionPayload } from '@/api/types'

const prefix = (workspaceId: string, targetId: string, resource: ResourceAuthorizationTargetType) =>
  `/workspace/${workspaceId}/resource_user_permission/resource/${targetId}/resource/${resource}`

/** 获取指定资源或文件夹的用户权限分页列表。 */
const getResourceAuthorization = (
  workspaceId: string,
  targetId: string,
  resource: ResourceAuthorizationTargetType,
  page: ParamsPage,
  query?: Dict<unknown>,
) => {
  return get<ResponsePage<ResourceUserPermission>>(`${prefix(workspaceId, targetId, resource)}/${page.currentPage}/${page.pageSize}`, query)
}

/** 更新资源的用户权限，可同时应用到有管理权限的子文件夹及资源。 */
const putResourceAuthorization = (
  workspaceId: string,
  targetId: string,
  resource: ResourceAuthorizationTargetType,
  permissions: ResourceUserPermissionPayload[],
) => {
  return put<ResourceUserPermissionPayload[], ResourceUserPermissionPayload[]>(prefix(workspaceId, targetId, resource), permissions)
}

export default { getResourceAuthorization, putResourceAuthorization }
