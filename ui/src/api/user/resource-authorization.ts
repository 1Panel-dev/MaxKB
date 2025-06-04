import { Result } from '@/request/Result'
import { get, put, post, del } from '@/request/index'
import type { pageRequest } from '@/api/type/common'
import type { Ref } from 'vue'

const prefix = '/workspace'

/**
 * 获取成员列表
 * @query 参数
 */
const getUserList: (workspace_id: String) => Promise<Result<any>> = (workspace_id) => {
  return get(`${prefix}/${workspace_id}/user_list`)
}

/**
 * 获取资源权限
 * @query 参数
 */
const getResourceAuthorization: (workspace_id: String, user_id: string) => Promise<Result<any>> = (
  workspace_id,
  user_id,
) => {
  return get(`${prefix}/${workspace_id}/user_resource_permission/user/${user_id}`)
}

/**
 * 修改成员权限
 * @param 参数 member_id
 * @param 参数 {
          "team_resource_permission_list": [
            {
              "auth_target_type": "KNOWLEDGE",
              "target_id": "string",
              "auth_type": "ROLE",
              "permission": {
                "VIEW": true,
                "MANAGE": true,
                "ROLE": true
              }
            }
          ]
        }
 */
const putResourceAuthorization: (
  workspace_id: String,
  user_id: string,
  body: any,
) => Promise<Result<any>> = (workspace_id, user_id, body) => {
  return put(`${prefix}/${workspace_id}/user_resource_permission/user/${user_id}`, body)
}

export default {
  getResourceAuthorization,
  putResourceAuthorization,
  getUserList,
}
