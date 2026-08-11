import { get, put } from '@/request/index'
import type { Result } from '@/request/Result'
import type { Ref } from 'vue'

const prefix = '/workspace'

/**
 * 获取资源授权 - 资源权限树
 */
const getResourceAuthorization = (
  workspace_id: string,
  user_id: string,
  resource: string,
  params?: any,
  loading?: Ref<boolean>,
): Promise<Result<any>> => {
  return get(
    `${prefix}/${workspace_id}/user_resource_permission/user/${user_id}/resource/${resource}`,
    params,
    loading,
  )
}

/**
 * 修改成员权限
 */
const putResourceAuthorization = (
  workspace_id: string,
  user_id: string,
  resource: string,
  body: any,
  loading?: Ref<boolean>,
): Promise<Result<any>> => {
  return put(
    `${prefix}/${workspace_id}/user_resource_permission/user/${user_id}/resource/${resource}`,
    body,
    loading,
  )
}

/**
 * 获取用户列表（工作空间下所有用户）
 */
const getUserList = (workspace_id: string, loading?: Ref<boolean>): Promise<Result<any>> => {
  return get(`${prefix}/${workspace_id}/user_list`, undefined, loading)
}

/**
 * 获取成员列表（工作空间下被授权的成员）
 */
const getUserMember = (workspace_id: string, loading?: Ref<boolean>): Promise<Result<any>> => {
  return get(`${prefix}/${workspace_id}/user_member`, undefined, loading)
}

export default {
  getResourceAuthorization,
  putResourceAuthorization,
  getUserList,
  getUserMember,
}
