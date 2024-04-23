import { Result } from '@/request/Result'
import { get, post, del, put } from '@/request/index'

import { type Ref } from 'vue'

const prefix = '/application'

/**
 * API_KEY列表
 * @param 参数 application_id
 */
const getAPIKey: (application_id: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  application_id,
  loading
) => {
  return get(`${prefix}/${application_id}/api_key`, undefined, loading)
}

/**
 * 新增API_KEY
 * @param 参数 application_id
 */
const postAPIKey: (application_id: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  application_id,
  loading
) => {
  return post(`${prefix}/${application_id}/api_key`, {}, undefined, loading)
}

/**
 * 删除API_KEY
 * @param 参数 application_id api_key_id
 */
const delAPIKey: (
  application_id: String,
  api_key_id: String,
  loading?: Ref<boolean>
) => Promise<Result<boolean>> = (application_id, api_key_id, loading) => {
  return del(`${prefix}/${application_id}/api_key/${api_key_id}`, undefined, undefined, loading)
}

/**
 * 修改API_KEY
 * @param 参数 application_id,api_key_id
 * data {
 *   is_active: boolean
 * }
 */
const putAPIKey: (
  application_id: string,
  api_key_id: String,
  data: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (application_id, api_key_id, data, loading) => {
  return put(`${prefix}/${application_id}/api_key/${api_key_id}`, data, undefined, loading)
}

/**
 * 统计
 * @param 参数 application_id, data
 */
const getStatistics: (
  application_id: string,
  data: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (application_id, data, loading) => {
  return get(`${prefix}/${application_id}/statistics/chat_record_aggregate_trend`, data, loading)
}

/**
 * 修改应用icon
 * @param 参数 application_id
 * data: file
 */
const putAppIcon: (
  application_id: string,
  data: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (application_id, data, loading) => {
  return put(`${prefix}/${application_id}/edit_icon`, data, undefined, loading)
}

export default {
  getAPIKey,
  postAPIKey,
  delAPIKey,
  putAPIKey,
  getStatistics,
  putAppIcon
}
