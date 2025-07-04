import { Result } from '@/request/Result'
import { get, put } from '@/request/index'
import { type Ref } from 'vue'

import useStore from '@/stores'
const prefix: any = { _value: '/workspace/' }
Object.defineProperty(prefix, 'value', {
  get: function () {
    const { user } = useStore()
    return this._value + user.getWorkspaceId() + '/application'
  },
})

/**
 * workflow历史版本
 */
const getWorkFlowVersion: (
  application_id: string,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (application_id, loading) => {
  return get(`${prefix.value}/${application_id}/application_version`, undefined, loading)
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
    `${prefix.value}/${application_id}/application_version/${application_version_id}`,
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
    `${prefix.value}/${application_id}/application_version/${application_version_id}`,
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
