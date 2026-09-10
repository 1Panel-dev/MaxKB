import { Result } from '@/request/Result'
import { get, put, post, del } from '@/request/index'
import type { Ref } from 'vue'
import type { pageRequest } from '@/api/type/common'
const prefix = '/workspace'

/** 获取引用当前资源的资源。 */
const getResourceDependents: (
  workspace_id: string,
  resource: string,
  resource_id: string,
  page: pageRequest,
  params?: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (workspace_id, resource, resource_id, page, params, loading) => {
  return get(`${prefix}/${workspace_id}/resource_mapping/${resource}/${resource_id}/${page.current_page}/${page.page_size}`, params, loading)
}
/** 获取当前资源依赖的资源。 */
const getResourceDependencies: (
  workspace_id: string,
  resource: string,
  resource_id: string,
  page: pageRequest,
  params?: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (workspace_id, resource, resource_id, page, params, loading) => {
  return get(`${prefix}/${workspace_id}/mapping_resource/${resource}/${resource_id}/${page.current_page}/${page.page_size}`, params, loading)
}

export default {
  getResourceDependents,
  getResourceDependencies,
}
