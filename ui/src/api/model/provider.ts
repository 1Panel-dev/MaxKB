import { Result } from '@/request/Result'
import { get, post } from '@/request/index'
import type { Ref } from 'vue'
import type { Provider } from '@/api/type/model'
import type { FormField } from '@/components/dynamics-form/type'
const prefix_provider = '/provider'
/**
 * 获得供应商列表
 */
const getProvider: (loading?: Ref<boolean>) => Promise<Result<Array<Provider>>> = (loading) => {
  return get(`${prefix_provider}`, {}, loading)
}

/**
 * 获得供应商列表
 */
const getProviderByModelType: (
  model_type: string,
  loading?: Ref<boolean>,
) => Promise<Result<Array<Provider>>> = (model_type, loading) => {
  return get(`${prefix_provider}`, { model_type }, loading)
}

/**
 * 获取模型创建表单
 * @param provider
 * @param model_type
 * @param model_name
 * @param loading
 * @returns
 */
const getModelCreateForm: (
  provider: string,
  model_type: string,
  model_name: string,
  loading?: Ref<boolean>,
) => Promise<Result<Array<FormField>>> = (provider, model_type, model_name, loading) => {
  return get(`${prefix_provider}/model_form`, { provider, model_type, model_name }, loading)
}
export default {
  getProvider,
  getModelCreateForm,
  getProviderByModelType,
}
