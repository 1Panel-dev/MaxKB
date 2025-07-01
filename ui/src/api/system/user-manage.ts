import {Result} from '@/request/Result'
import {get, put, post, del} from '@/request/index'
import type {pageRequest} from '@/api/type/common'
import type {Ref} from 'vue'


const prefix = '/user_manage'
/**
 * 用户分页列表
 * @query 参数
 email_or_username: string
 */
const getUserManage: (
  page: pageRequest,
  params?: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (page, params, loading) => {
  return get(
    `${prefix}/${page.current_page}/${page.page_size}`,
    params ? params : undefined,
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
 * 获取系统默认密码
 */
const getSystemDefaultPassword: (
  loading?: Ref<boolean>
) => Promise<Result<string>> = (loading) => {
  return get('/user_manage/password', undefined, loading)
}


/**
 * 获取校验
 * @param valid_type 校验类型: application|knowledge|user
 * @param valid_count 校验数量: 5 | 50 | 2
 */
const getValid: (
  valid_type: string,
  valid_count: number,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (valid_type, valid_count, loading) => {
  return get(`/valid/${valid_type}/${valid_count}`, undefined, loading)
}


export default {
  getUserManage,
  putUserManage,
  delUserManage,
  postUserManage,
  putUserManagePassword,
  getSystemDefaultPassword,
  getValid,

}
