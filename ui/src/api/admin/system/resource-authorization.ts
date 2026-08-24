import { get, put } from '../core/request'
import type {
  RequestParams,
  ResourceAuthorizationType,
  ResourcePermissionItem,
  ResourcePermissionPayload,
} from '@/api/types'

const prefix = (workspaceId: string, userId: string, resource: ResourceAuthorizationType) =>
  `/workspace/${workspaceId}/user_resource_permission/user/${userId}/resource/${resource}`

/** 获取工作空间成员对指定类型资源的权限列表。 */
const getUserResourcePermissions = (
  workspaceId: string,
  userId: string,
  resource: ResourceAuthorizationType,
  query?: RequestParams,
) => {
  return get<ResourcePermissionItem[]>(prefix(workspaceId, userId, resource), query)
}

/** 更新工作空间成员对指定类型资源的权限。 */
const putUserResourcePermissions = (
  workspaceId: string,
  userId: string,
  resource: ResourceAuthorizationType,
  permissions: ResourcePermissionPayload[],
) => {
  return put<ResourcePermissionPayload[], ResourcePermissionPayload[]>(
    prefix(workspaceId, userId, resource),
    permissions,
  )
}

export default {
  getUserResourcePermissions,
  putUserResourcePermissions,
}
