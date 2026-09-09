import { get, put } from '../core/request'
import type { ParamsPage, ResponsePage } from '../core/types'
import type {
  Dict,
  ResourceUserGroupPermission,
  ResourceUserGroupPermissionPayload,
  ResourceAuthorizationTargetType,
  ResourceUserPermission,
  ResourceUserPermissionPayload,
} from '@/api/types'
import { getWorkspaceId } from '@/utils/resource-context'

const getPrefix = () => {
  const workspaceId = getWorkspaceId()
  return `/workspace/${workspaceId}`
}
/** 获取指定资源或文件夹的用户权限分页列表。 */
const getResourceAuthorization = (targetId: string, resource: ResourceAuthorizationTargetType, page: ParamsPage, query?: Dict<unknown>) => {
  return get<ResponsePage<ResourceUserPermission>>(
    `${getPrefix()}/resource_user_permission/resource/${targetId}/resource/${resource}/${page.currentPage}/${page.pageSize}`,
    query,
  )
}

/** 更新资源的用户权限，可同时应用到有管理权限的子文件夹及资源。 */
const putResourceAuthorization = (targetId: string, resource: ResourceAuthorizationTargetType, permissions: ResourceUserPermissionPayload[]) => {
  return put<ResourceUserPermissionPayload[], ResourceUserPermissionPayload[]>(
    `${getPrefix()}/resource_user_permission/resource/${targetId}/resource/${resource}`,
    permissions,
  )
}

/** 获取指定资源或文件夹的用户组权限分页列表。 */
const getResourceUserGroupAuthorization = (targetId: string, resource: ResourceAuthorizationTargetType, page: ParamsPage, query?: Dict<unknown>) => {
  return get<ResponsePage<ResourceUserGroupPermission>>(
    `${getPrefix()}/resource_user_group_permission/resource/${targetId}/resource/${resource}/${page.currentPage}/${page.pageSize}`,
    query,
  )
}

/** 更新资源的用户组权限，可应用到有管理权限的子文件夹及资源。 */
const putResourceUserGroupAuthorization = (
  targetId: string,
  resource: ResourceAuthorizationTargetType,
  permissions: ResourceUserGroupPermissionPayload[],
) => {
  return put<ResourceUserGroupPermissionPayload[], ResourceUserGroupPermissionPayload[]>(
    `${getPrefix()}/resource_user_group_permission/resource/${targetId}/resource/${resource}`,
    permissions,
  )
}

export default { getResourceAuthorization, putResourceAuthorization, getResourceUserGroupAuthorization, putResourceUserGroupAuthorization }
