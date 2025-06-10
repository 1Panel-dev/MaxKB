import { Result } from '@/request/Result'
import { get, post, postStream, del, put, request, download, exportFile } from '@/request/index'
import type { pageRequest } from '@/api/type/common'
import type { ApplicationFormType } from '@/api/type/application'
import { type Ref } from 'vue'
import type { FormField } from '@/components/dynamics-form/type'

const prefix = '/workspace/' + localStorage.getItem('workspace_id') + '/application'

/**
 * 获取全部应用
 * @param 参数
 */
const getAllApplication: (param?: any, loading?: Ref<boolean>) => Promise<Result<any[]>> = (
  param,
  loading,
) => {
  return get(`${prefix}`, param, loading)
}

/**
 * 获取分页应用
 * param {
 "name": "string",
 }
 */
const getApplication: (
  page: pageRequest,
  param: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (page, param, loading) => {
  return get(`${prefix}/${page.current_page}/${page.page_size}`, param, loading)
}

/**
 * 创建应用
 * @param 参数
 */
const postApplication: (
  data: ApplicationFormType,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (data, loading) => {
  return post(`${prefix}`, data, undefined, loading)
}

/**
 * 修改应用
 * @param 参数
 */
const putApplication: (
  application_id: string,
  data: ApplicationFormType,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (application_id, data, loading) => {
  return put(`${prefix}/${application_id}`, data, undefined, loading)
}

/**
 * 删除应用
 * @param 参数 application_id
 */
const delApplication: (
  application_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<boolean>> = (application_id, loading) => {
  return del(`${prefix}/${application_id}`, undefined, {}, loading)
}

/**
 * 应用详情
 * @param 参数 application_id
 */
const getApplicationDetail: (
  application_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (application_id, loading) => {
  return get(`${prefix}/${application_id}`, undefined, loading)
}

/**
 * 获取AccessToken
 * @param 参数 application_id
 */
const getAccessToken: (application_id: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  application_id,
  loading,
) => {
  return get(`${prefix}/${application_id}/access_token`, undefined, loading)
}

/**
 * 修改AccessToken
 * @param 参数 application_id
 * data {
 *  "is_active": true
 * }
 */
const putAccessToken: (
  application_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (application_id, data, loading) => {
  return put(`${prefix}/${application_id}/access_token`, data, undefined, loading)
}

/**
 * 导出应用
 */

const exportApplication = (
  application_id: string,
  application_name: string,
  loading?: Ref<boolean>,
) => {
  return exportFile(
    application_name + '.mk',
    `${prefix}/${application_id}/export`,
    undefined,
    loading,
  )
}

/**
 * 导入应用
 */
const importApplication: (data: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  data,
  loading,
) => {
  return post(`${prefix}/import`, data, undefined, loading)
}

/**
 * 统计
 * @param 参数 application_id, data
 */
const getStatistics: (
  application_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (application_id, data, loading) => {
  return get(`${prefix}/${application_id}/application-stats`, data, loading)
}

export default {
  getAllApplication,
  getApplication,
  postApplication,
  putApplication,
  delApplication,
  getApplicationDetail,
  getAccessToken,
  putAccessToken,
  exportApplication,
  importApplication,
  getStatistics,
}
