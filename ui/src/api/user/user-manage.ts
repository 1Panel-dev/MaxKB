import { Result } from '@/request/Result'
import { get, put, post, del } from '@/request/index'
import type { pageRequest } from '@/api/type/common'
import type { Ref } from 'vue'
import type {ResetPasswordRequest} from "@/api/type/user.ts";

const prefix = '/user_manage'
/**
 * 用户分页列表
 * @query 参数
   email_or_username: string
 */
const getUserManage: (
  page: pageRequest,
  email_or_username: string,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (page, email_or_username, loading) => {
  return get(
    `${prefix}/${page.current_page}/${page.page_size}`,
    email_or_username ? { email_or_username } : undefined,
    loading,
  )
}

/**
 * 删除用户
 * @param 参数 user_id,
 */
const delUserManage: (user_id: string, loading?: Ref<boolean>) => Promise<Result<boolean>> = (
  user_id,
  loading,
) => {
  return del(`${prefix}/${user_id}`, undefined, {}, loading)
}

/**
 * 创建用户
 */
const postUserManage: (data: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  data,
  loading,
) => {
  return post(`${prefix}`, data, undefined, loading)
}

/**
 * 编辑用户
 */
const putUserManage: (
  user_id: string,
  data: any,
  loading?: Ref<boolean>,
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

/**
 * 重置密码
 * @param request 重置密码请求参数
 * @param loading 接口加载器
 * @returns
 */
const resetPassword: (
  request: ResetPasswordRequest,
  loading?: Ref<boolean>
) => Promise<Result<boolean>> = (request, loading) => {
  return post('/user/re_password', request, undefined, loading)
}

export default {
  getUserManage,
  putUserManage,
  delUserManage,
  postUserManage,
  putUserManagePassword,
  resetPassword
}
