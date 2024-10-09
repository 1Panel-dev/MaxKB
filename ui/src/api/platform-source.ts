import { Result } from '@/request/Result'
import { get, post, del, put } from '@/request/index'
import type { pageRequest } from '@/api/type/common'
import { type Ref } from 'vue'

const prefix = '/platform'
const getPlatformInfo: (loading?: Ref<boolean>) => Promise<Result<any>> = (loading) => {
  return get(`${prefix}/source`, undefined, loading)
}

const updateConfig: (data: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  data,
  loading
) => {
  return post(`${prefix}/source`, data, undefined, loading)
}

const validateConnection: (data: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  data,
  loading
) => {
  return put(`${prefix}/source`, data, undefined, loading)
}
export default {
  getPlatformInfo,
  updateConfig,
  validateConnection
}
