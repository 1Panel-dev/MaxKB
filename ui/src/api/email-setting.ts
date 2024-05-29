import { Result } from '@/request/Result'
import { get, post, del, put } from '@/request/index'
import type { pageRequest } from '@/api/type/common'
import { type Ref } from 'vue'

const prefix = '/email_setting'
/**
 * 獲取郵箱設置
 */
const getEmailSetting: (loading?: Ref<boolean>) => Promise<Result<any>> = (loading) => {
  return get(`${prefix}`, undefined, loading)
}

/**
 * 郵箱測試
 */
const postTestEmail: (data: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  data,
  loading
) => {
  return post(`${prefix}`, data, undefined, loading)
}

/**
 * 修改郵箱設置
 */
const putEmailSetting: (data: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  data,
  loading
) => {
  return put(`${prefix}`, data, undefined, loading)
}

export default {
  getEmailSetting,
  postTestEmail,
  putEmailSetting
}
