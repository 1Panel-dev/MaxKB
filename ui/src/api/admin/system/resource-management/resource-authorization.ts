import { get, put } from '../../core/request'
import type { ParamsPage, ResponsePage } from '../../core/types'
import type {
  Dict,
  ResourceAuthorizationTargetType,
  ResourceUserGroupPermission,
  ResourceUserGroupPermissionPayload,
  ResourceUserPermission,
  ResourceUserPermissionPayload,
} from '@/api/types'

const getPrefix = (workspaceId: string) => `/system/workspace/${workspaceId}/resource_management`

/** 获取 System 资源管理中指定资源或文件夹的用户权限分页列表。 */
const getResourceAuthorization = (
  workspaceId: string,
  targetId: string,
  resource: ResourceAuthorizationTargetType,
  page: ParamsPage,
  query?: Dict<unknown>,
) => {
  return get<ResponsePage<ResourceUserPermission>>(
    `${getPrefix(workspaceId)}/resource/${targetId}/resource/${resource}/${page.currentPage}/${page.pageSize}`,
    query,
  )
}

/** 更新 System 资源管理中的用户权限及文件夹生效范围。 */
const putResourceAuthorization = (
  workspaceId: string,
  targetId: string,
  resource: ResourceAuthorizationTargetType,
  permissions: ResourceUserPermissionPayload[],
) => {
  return put<ResourceUserPermissionPayload[], ResourceUserPermissionPayload[]>(
    `${getPrefix(workspaceId)}/resource/${targetId}/resource/${resource}`,
    permissions,
  )
}

/** 获取 System 资源管理中指定资源或文件夹的用户组权限分页列表。 */
const getResourceUserGroupAuthorization = (
  workspaceId: string,
  targetId: string,
  resource: ResourceAuthorizationTargetType,
  page: ParamsPage,
  query?: Dict<unknown>,
) => {
  return get<ResponsePage<ResourceUserGroupPermission>>(
    `${getPrefix(workspaceId)}/user_group_resource/${targetId}/resource/${resource}/${page.currentPage}/${page.pageSize}`,
    query,
  )
}

/** 更新 System 资源管理中的用户组权限及文件夹生效范围。 */
const putResourceUserGroupAuthorization = (
  workspaceId: string,
  targetId: string,
  resource: ResourceAuthorizationTargetType,
  permissions: ResourceUserGroupPermissionPayload[],
) => {
  return put<ResourceUserGroupPermissionPayload[], ResourceUserGroupPermissionPayload[]>(
    `${getPrefix(workspaceId)}/user_group_resource/${targetId}/resource/${resource}`,
    permissions,
  )
}

export default {
  getResourceAuthorization,
  putResourceAuthorization,
  getResourceUserGroupAuthorization,
  putResourceUserGroupAuthorization,
}
