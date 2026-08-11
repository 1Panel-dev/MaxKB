import { get, put, post, del } from '@/request/index'
import type { Result } from '@/request/Result'
import type { Ref } from 'vue'

const prefix = '/user_manage'

const getUserManage = (
  page: { current_page: number; page_size: number },
  params?: any,
  loading?: Ref<boolean>,
): Promise<Result<any>> => {
  return get(`${prefix}/${page.current_page}/${page.page_size}`, params, loading)
}

const delUserManage = (user_id: string, loading?: Ref<boolean>): Promise<Result<boolean>> => {
  return del(`${prefix}/${user_id}`, loading)
}

const postUserManage = (data: any, loading?: Ref<boolean>): Promise<Result<any>> => {
  return post(`${prefix}`, data, undefined, loading)
}

const putUserManage = (
  user_id: string,
  data: any,
  loading?: Ref<boolean>,
): Promise<Result<any>> => {
  return put(`${prefix}/${user_id}`, data, loading)
}

const putUserManagePassword = (
  user_id: string,
  data: any,
  loading?: Ref<boolean>,
): Promise<Result<any>> => {
  return put(`${prefix}/${user_id}/re_password`, data, loading)
}

const getSystemDefaultPassword = (loading?: Ref<boolean>): Promise<Result<string>> => {
  return get('/user_manage/password', undefined, loading)
}

const batchDelete = (ids: string[], loading?: Ref<boolean>): Promise<Result<any>> => {
  return post(`/user_manage/batch_delete`, ids, {}, loading)
}

export default {
  getUserManage,
  putUserManage,
  delUserManage,
  postUserManage,
  putUserManagePassword,
  getSystemDefaultPassword,
  batchDelete,
}
