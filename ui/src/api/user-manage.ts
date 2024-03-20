import { Result } from '@/request/Result'
import { get, post, del, put } from '@/request/index'
import type { pageRequest } from '@/api/type/common'
import { type Ref } from 'vue'

const prefix = '/user_manage'
/**
 * 用户分页列表
 * @param 参数 
 * page  {
              "current_page": "string",
              "page_size": "string",
            }
 * @query 参数 
   email_or_username: string
 */
const getUserManage: (
  page: pageRequest,
  email_or_username: string,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (page, email_or_username, loading) => {
  return get(
    `${prefix}/${page.current_page}/${page.page_size}`,
    email_or_username ? { email_or_username } : undefined,
    loading
  )
}

/**
 * 删除用户
 * @param 参数 user_id,
 */
const delUserManage: (user_id: string, loading?: Ref<boolean>) => Promise<Result<boolean>> = (
  user_id,
  loading
) => {
  return del(`${prefix}/${user_id}`, undefined, {}, loading)
}

/**
 * 创建用户
 */
const postUserManage: (data: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  data,
  loading
) => {
  return post(`${prefix}`, data, undefined, loading)
}

/**
 * 编辑用户
 */
const putUserManage: (
  user_id: string,
  data: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (user_id, data, loading) => {
  return put(`${prefix}/${user_id}`, data, undefined, loading)
}
/**
 * 修改用户密码
 */
const putUserManagePassword: (
  user_id: string,
  data: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (user_id, data, loading) => {
  return put(`${prefix}/${user_id}/re_password`, data, undefined, loading)
}

export default {
  getUserManage,
  delUserManage,
  postUserManage,
  putUserManage,
  putUserManagePassword
}
