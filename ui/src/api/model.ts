import { Result } from '@/request/Result'
import { get, post, del, put } from '@/request/index'
import { type Ref } from 'vue'
import type { modelRequest, Provider } from '@/api/type/model'
const prefix = '/model'
const prefix_provider = '/provider'

/**
 * 获得模型列表
 * @params 参数 name, model_type, model_name
 */
const getModel: (data?: modelRequest) => Promise<Result<any>> = (data) => {
  return get(`${prefix}`, data)
}
/**
 * 获得供应商列表
 */
const getProvider: (loading?: Ref<boolean>) => Promise<Result<Array<Provider>>> = (loading) => {
  return get(`${prefix_provider}`, {}, loading)
}

export default {
  getModel,
  getProvider
}
