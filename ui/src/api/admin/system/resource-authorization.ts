import { get, put } from '../core/request'
import type { Dict, ResourceAuthorizationType, ResourcePermissionItem, ResourcePermissionPayload } from '@/api/types'

/** 系统管理资源授权 */
const prefix = (workspaceId: string) => `/workspace/${workspaceId}/user_resource_permission`
/** 获取指定空间、指定用户、指定资源类型的权限列表。 */
const getUserResourcePermissions = (workspaceId: string, userId: string, resource: ResourceAuthorizationType, query?: Dict<unknown>) => {
  return get<ResourcePermissionItem[]>(`${prefix(workspaceId)}/user/${userId}/resource/${resource}`, query)
}

/** 更新指定空间、指定用户、指定资源类型的权限列表。 */
const putUserResourcePermissions = (workspaceId: string, userId: string, resource: ResourceAuthorizationType, permissions: ResourcePermissionPayload[]) => {
  return put<ResourcePermissionPayload[], ResourcePermissionPayload[]>(`${prefix(workspaceId)}/user/${userId}/resource/${resource}`, permissions)
}

export default { getUserResourcePermissions, putUserResourcePermissions }
