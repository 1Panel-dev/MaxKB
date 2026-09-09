import { get, put } from '../../core/request'
import type { ParamsPage, ResponsePage } from '../../core/types'
import type { Dict, ResourceAuthorizationTargetType, ResourceUserPermission, ResourceUserPermissionPayload } from '@/api/types'
import { getWorkspaceId } from '@/utils/resource-context'

const getPrefix = () => `/system/workspace/${getWorkspaceId()}/resource_management`

/** 获取 System 资源管理中指定资源或文件夹的用户权限分页列表。 */
const getResourceAuthorization = (targetId: string, resource: ResourceAuthorizationTargetType, page: ParamsPage, query?: Dict<unknown>) => {
  return get<ResponsePage<ResourceUserPermission>>(
    `${getPrefix()}/resource/${targetId}/resource/${resource}/${page.currentPage}/${page.pageSize}`,
    query,
  )
}

/** 更新 System 资源管理中的用户权限及文件夹生效范围。 */
const putResourceAuthorization = (targetId: string, resource: ResourceAuthorizationTargetType, permissions: ResourceUserPermissionPayload[]) => {
  return put<ResourceUserPermissionPayload[], ResourceUserPermissionPayload[]>(
    `${getPrefix()}/resource/${targetId}/resource/${resource}`,
    permissions,
  )
}

export default { getResourceAuthorization, putResourceAuthorization }
