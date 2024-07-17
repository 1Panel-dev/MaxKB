import { Result } from '@/request/Result'
import { get, post, del, put } from '@/request/index'
import { type Ref } from 'vue'

const prefix = '/license'

/**
 * 获得license信息
 */
const getLicense: (loading?: Ref<boolean>) => Promise<Result<any>> = (loading) => {
  return get(`${prefix}/profile`, undefined, loading)
}
/**
 * 更新license信息
 * @param 参数  license_file:file
 */
const putLicense: (data: any, loading?: Ref<boolean>) => Promise<Result<any>> = (data, loading) => {
  return put(`${prefix}/profile`, data, undefined, loading)
}

export default {
  getLicense,
  putLicense
}
