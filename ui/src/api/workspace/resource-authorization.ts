import { Result } from '@/request/Result'
import { get, put, post, del } from '@/request/index'
import type { Ref } from 'vue'
import type { pageRequest } from '@/api/type/common'
const prefix = '/workspace'


/**
 * 工作空间下各资源获取资源权限
 * @query 参数
 */
const getResourceAuthorization: (
  workspace_id: string,
  target: string,
  resource: string,
  page: pageRequest,
  params?: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (workspace_id, target, resource, page, params, loading) => {
  return get(
    `${prefix}/${workspace_id}/resource_user_permission/resource/${target}/resource/${resource}/${page.current_page}/${page.page_size}`,
    params,
    loading,
  )
}

/**
 * 工作空间下各资源修改成员权限
 * @param 参数 member_id
 * @param 参数 {
     [
      {
        "user_id": "string",
        "permission": "NOT_AUTH"
      }
    ]
  }
 */
const putResourceAuthorization: (
  workspace_id: string,
  target: string,
  resource: string,
  body: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (workspace_id, target, resource, body, loading) => {
  return put(
    `${prefix}/${workspace_id}/resource_user_permission/resource/${target}/resource/${resource}`,
    body,
    {},
    loading,
  )
}

export default {
  getResourceAuthorization,
  putResourceAuthorization
}
