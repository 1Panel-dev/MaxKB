import { get, post } from './core/request'
import type { BaseModelOption, DynamicFormField, ModelProviderItem, ModelTypeOption } from '@/api/types'

const prefix = '/provider'

/** 获取模型供应商，可按模型类型筛选。 */
const getProviderList = (query?: { model_type?: string }) => {
  return get<ModelProviderItem[]>(prefix, query)
}

/** 获取创建模型所需的动态表单。 */
const getModelCreateForm = (provider: string, modelType: string, modelName: string) => {
  return get<DynamicFormField[]>(`${prefix}/model_form`, { model_name: modelName, model_type: modelType, provider })
}

/** 获取基础模型的动态参数表单。 */
const getBaseModelParamsForm = (provider: string, modelType: string, modelName: string) => {
  return get<DynamicFormField[]>(`${prefix}/model_params_form`, { model_name: modelName, model_type: modelType, provider })
}

/** 获取供应商支持的模型类型。 */
const getModelTypeList = (provider: string) => {
  return get<ModelTypeOption[]>(`${prefix}/model_type_list`, { provider })
}

/** 获取供应商指定类型下的基础模型，可携带 search 远程筛选；提供凭证时后端实时查询官方模型列表。 */
const getBaseModelList = (provider: string, modelType: string, search?: string, credential?: Record<string, unknown>) => {
  // 携带凭证时走 POST body，避免 api_key 泄露到 URL/访问日志。
  if (credential && Object.keys(credential).length > 0) {
    return post<Record<string, unknown>, BaseModelOption[]>(`${prefix}/model_list`, {
      model_type: modelType,
      provider,
      search,
      ...credential,
      credential,
    })
  }
  return get<BaseModelOption[]>(`${prefix}/model_list`, { model_type: modelType, provider, search })
}

/** 按「url + key」读取后端缓存的基础模型列表，未命中返回空数组；编辑时传 modelId，由后端用真实凭证取缓存。 */
const getBaseModelListCache = (
  provider: string,
  modelType: string,
  credential: Record<string, unknown>,
  modelId?: string,
) => {
  return post<Record<string, unknown>, BaseModelOption[]>(`${prefix}/model_list_cache`, {
    model_type: modelType,
    model_id: modelId,
    provider,
    ...credential,
    credential,
  })
}

export default { getBaseModelList, getBaseModelListCache, getBaseModelParamsForm, getModelCreateForm, getModelTypeList, getProviderList }
