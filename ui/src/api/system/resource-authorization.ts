import { Result } from '@/request/Result'
import { get, put, post, del } from '@/request/index'
import type { Ref } from 'vue'
import type { pageRequest } from '@/api/type/common'
const prefix = '/workspace'

/**
 * 系统资源授权获取资源权限
 * @query 参数
 */
const getResourceAuthorization: (
  workspace_id: string,
  user_id: string,
  resource: string,
  params?: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (workspace_id, user_id, resource, params, loading) => {
  return get(
    `${prefix}/${workspace_id}/user_resource_permission/user/${user_id}/resource/${resource}`,
    params,
    loading,
  )
}

/**
 * 系统资源授权修改成员权限
 * @param 参数 member_id
 * @param 参数 {
     [
      {
        "target_id": "string",
        "permission": "NOT_AUTH"
      }
    ]
        }
 */
const putResourceAuthorization: (
  workspace_id: string,
  user_id: string,
  resource: string,
  body: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (workspace_id, user_id, resource, body, loading) => {
  return put(
    `${prefix}/${workspace_id}/user_resource_permission/user/${user_id}/resource/${resource}`,
    body,
    {},
    loading,
  )
}

/**
 * 获取成员列表
 * @query 参数
 */
const getUserList: (workspace_id: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  workspace_id,
  loading,
) => {
  return get(`${prefix}/${workspace_id}/user_list`, undefined, loading)
}

const getUserMember: (workspace_id: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  workspace_id,
  loading,
) => {
  return get(`${prefix}/${workspace_id}/user_member`, undefined, loading)
}

/**
 * 获得系统文件夹列表
 * @params 参数
 *  source : APPLICATION, KNOWLEDGE, TOOL
 *  data : {name: string}
 */
const getSystemFolder: (
  workspace_id: string,
  source: string,
  data?: any,
  loading?: Ref<boolean>,
) => Promise<Result<Array<any>>> = (workspace_id, source, data, loading) => {
  if (source == 'MODEL') {
    return Promise.resolve(
      Result.success([
        {
          id: 'default',
          name: '根目录',
          desc: null,
          parent_id: null,
          children: [],
        },
      ]),
    )
  }
  return get(`${prefix}/${workspace_id}/${source}/folder`, data, loading)
}

export default {
  getResourceAuthorization,
  putResourceAuthorization,
  getUserList,
  getUserMember,
  getSystemFolder,

}
