import { Result } from '@/request/Result'
import { get, put, post, del } from '@/request/index'
import type { Ref } from 'vue'
import type { pageRequest } from '@/api/type/common'
const prefix = '/workspace'

/**
 * 工作空间下各个资源的映射关系
 * @query 参数
 */
const getResourceMapping: (
  workspace_id: string,
  resource: string,
  resource_id: string,
  page: pageRequest,
  params?: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (workspace_id, resource, resource_id, page, params, loading) => {
  return get(
    `${prefix}/${workspace_id}/resource_mapping/${resource}/${resource_id}/${page.current_page}/${page.page_size}`,
    params,
    loading,
  )
}
/**
 * 依赖项
 * @param workspace_id
 * @param resource
 * @param resource_id
 * @param page
 * @param params
 * @param loading
 * @returns
 */
const getMappingResource: (
  workspace_id: string,
  resource: string,
  resource_id: string,
  page: pageRequest,
  params?: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (workspace_id, resource, resource_id, page, params, loading) => {
  return get(
    `${prefix}/${workspace_id}/mapping_resource/${resource}/${resource_id}/${page.current_page}/${page.page_size}`,
    params,
    loading,
  )
}

export default {
  getResourceMapping,
  getMappingResource,
}
