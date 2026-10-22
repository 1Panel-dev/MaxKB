import { get, post } from '../../core/request'
import type { SharedResourceType, SharedWorkspaceAuthorization } from '@/api/types'

const prefix = '/system/shared'

/** 获取共享资源的工作空间授权配置。 */
const getSharedAuthorization = (resourceType: SharedResourceType, resourceId: string) => {
  return get<SharedWorkspaceAuthorization | null>(`${prefix}/${resourceType.toLowerCase()}/${resourceId}/authorization`)
}

/** 保存共享资源的工作空间授权配置。 */
const postSharedAuthorization = (resourceType: SharedResourceType, resourceId: string, payload: SharedWorkspaceAuthorization) => {
  return post<SharedWorkspaceAuthorization, boolean>(`${prefix}/${resourceType.toLowerCase()}/${resourceId}/authorization`, payload)
}

export default { getSharedAuthorization, postSharedAuthorization }
