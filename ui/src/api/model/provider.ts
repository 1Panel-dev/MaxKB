import type { Result } from '@/request/Result'
import { get } from '@/request/index'
import type { Ref } from 'vue'
import type { Provider, BaseModel } from '@/api/type/model'
import type { FormField } from '@/api/type/common'

const prefix_provider = '/provider'

const getProvider: (loading?: Ref<boolean>) => Promise<Result<Array<Provider>>> = (loading) => {
  return get(`${prefix_provider}`, {}, loading)
}

const getProviderByModelType: (
  model_type: string,
  loading?: Ref<boolean>,
) => Promise<Result<Array<Provider>>> = (model_type, loading) => {
  return get(`${prefix_provider}`, { model_type }, loading)
}

const getModelCreateForm: (
  provider: string,
  model_type: string,
  model_name: string,
  loading?: Ref<boolean>,
) => Promise<Result<Array<FormField>>> = (provider, model_type, model_name, loading) => {
  return get(`${prefix_provider}/model_form`, { provider, model_type, model_name }, loading)
}

const listModelType: (
  provider: string,
  loading?: Ref<boolean>,
) => Promise<Result<Array<{ key: string; value: string }>>> = (provider, loading) => {
  return get(`${prefix_provider}/model_type_list`, { provider }, loading)
}

const listBaseModel: (
  provider: string,
  model_type: string,
  loading?: Ref<boolean>,
) => Promise<Result<Array<BaseModel>>> = (provider, model_type, loading) => {
  return get(`${prefix_provider}/model_list`, { provider, model_type }, loading)
}

const listBaseModelParamsForm: (
  provider: string,
  model_type: string,
  model_name: string,
  loading?: Ref<boolean>,
) => Promise<Result<Array<any>>> = (provider, model_type, model_name, loading) => {
  return get(`${prefix_provider}/model_params_form`, { provider, model_type, model_name }, loading)
}

export default {
  getProvider,
  getModelCreateForm,
  getProviderByModelType,
  listModelType,
  listBaseModel,
  listBaseModelParamsForm,
}
