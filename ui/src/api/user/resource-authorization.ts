import { Result } from '@/request/Result'
import { get, put, post, del } from '@/request/index'
import type { pageRequest } from '@/api/type/common'
import type { Ref } from 'vue'

import useStore from '@/stores'
const prefix: any = { _value: '/workspace/' }
Object.defineProperty(prefix, 'value', {
  get: function () {
    const { user } = useStore()
    return this._value + user.getWorkspaceId()
  },
})

/**
 * 获取成员列表
 * @query 参数
 */
const getUserList: (loading?: Ref<boolean>) => Promise<Result<any>> = (loading) => {
  return get(`${prefix.value}/user_list`, undefined, loading)
}

/**
 * 获取资源权限
 * @query 参数
 */
const getResourceAuthorization: (
  user_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (user_id, loading) => {
  return get(`${prefix.value}/user_resource_permission/user/${user_id}`, undefined, loading)
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
  user_id: string,
  body: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (user_id, body, loading) => {
  return put(`${prefix.value}/user_resource_permission/user/${user_id}`, body, loading)
}
const getUserMember: (loading?: Ref<boolean>) => Promise<Result<any>> = (loading) => {
  return get(`${prefix.value}/user_member`, undefined, loading)
}
export default {
  getResourceAuthorization,
  putResourceAuthorization,
  getUserList,
  getUserMember,
}
