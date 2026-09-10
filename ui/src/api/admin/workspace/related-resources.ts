import { get } from '../core/request'
import type { ParamsPage, ResponsePage } from '../core/types'
import type { Dict, RelatedResource, ResourceType } from '@/api/types'

/** 获取引用当前资源的资源。 */
const getResourceDependents = (workspaceId: string, resource: ResourceType, resourceId: string, page: ParamsPage, query?: Dict<unknown>) => {
  return get<ResponsePage<RelatedResource>>(
    `/workspace/${workspaceId}/resource_mapping/${resource}/${resourceId}/${page.currentPage}/${page.pageSize}`,
    query,
  )
}

/** 获取当前资源依赖的资源。 */
const getResourceDependencies = (workspaceId: string, resource: ResourceType, resourceId: string, page: ParamsPage, query?: Dict<unknown>) => {
  return get<ResponsePage<RelatedResource>>(
    `/workspace/${workspaceId}/mapping_resource/${resource}/${resourceId}/${page.currentPage}/${page.pageSize}`,
    query,
  )
}

export default { getResourceDependents, getResourceDependencies }
