import { Result } from '@/request/Result'
import { get, put } from '@/request/index'
import { type Ref } from 'vue'

const prefix = '/system/resource/application'

/**
 * workflow历史版本
 */
const getWorkFlowVersion: (
  application_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (application_id, loading) => {
  return get(`${prefix}/${application_id}/application_version`, undefined, loading)
}

/**
 * workflow历史版本详情
 */
const getWorkFlowVersionDetail: (
  application_id: string,
  application_version_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (application_id, application_version_id, loading) => {
  return get(
    `${prefix}/${application_id}/application_version/${application_version_id}`,
    undefined,
    loading,
  )
}
/**
 * 修改workflow历史版本
 */
const putWorkFlowVersion: (
  application_id: string,
  application_version_id: string,
  data: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (application_id, application_version_id, data, loading) => {
  return put(
    `${prefix}/${application_id}/application_version/${application_version_id}`,
    data,
    undefined,
    loading,
  )
}
export default {
  getWorkFlowVersion,
  getWorkFlowVersionDetail,
  putWorkFlowVersion,
}
