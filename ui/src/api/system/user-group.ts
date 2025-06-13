import {Result} from '@/request/Result'
import {get, post, del, put} from '@/request/index'
import type {Ref} from 'vue'

const prefix = '/system/group'

/**
 * 获取用户组列表
 */
const getUserGroup: (loading?: Ref<boolean>) => Promise<Result<any[]>> = () => {
  return get(`${prefix}`)
}

/**
 * 创建用户组
 * @param 参数
 * {
 "id": "string",
 "name": "string"
 }
 */
const postUserGroup: (data: any, loading?: Ref<boolean>) => Promise<Result<boolean>> = (
  data,
  loading,
) => {
  return post(`${prefix}`, data, undefined, loading)
}

/**
 * 删除用户组
 * @param 参数 user_group_id
 */
const delUserGroup: (user_group_id: String, loading?: Ref<boolean>) => Promise<Result<boolean>> = (
  user_group_id,
  loading,
) => {
  return del(`${prefix}/${user_group_id}`, undefined, {}, loading)
}

/**
 * 给用户组添加用户
 * @param 参数
 * {
 "additionalProp1": "string",
 "additionalProp2": "string",
 "additionalProp3": "string"
 }
 */
const postAddMember: (
  user_group_id: string,
  body: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (user_group_id, body, loading) => {
  return post(`${prefix}/${user_group_id}/add_member`, body, {}, loading)
}

/**
 * 从用户组删除用户
 * @param 参数 {
 "additionalProp1": "string",
 "additionalProp2": "string",
 "additionalProp3": "string"
 }
 */
const postRemoveMember: (
  user_group_id: string,
  body: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (user_group_id, body, loading) => {
  return post(`${prefix}/${user_group_id}`, body, {}, loading)
}

export default {
  getUserGroup,
  postUserGroup,
  delUserGroup,
  postAddMember,
  postRemoveMember,
}
