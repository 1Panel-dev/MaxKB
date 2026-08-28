import { get } from '../../core/request'
import type {
  BaseModelOption,
  DynamicFormField,
  ModelProviderItem,
  ModelTypeOption,
} from '@/api/types'

const prefix = '/provider'

/** 获取全部模型供应商。 */
const getProviderList = () => {
  return get<ModelProviderItem[]>(prefix)
}

/** 获取支持指定模型类型的供应商。 */
const getProviderListByModelType = (modelType: string) => {
  return get<ModelProviderItem[]>(prefix, { model_type: modelType })
}

/** 获取创建模型所需的动态表单。 */
const getModelCreateForm = (provider: string, modelType: string, modelName: string) => {
  return get<DynamicFormField[]>(`${prefix}/model_form`, {
    model_name: modelName,
    model_type: modelType,
    provider,
  })
}

/** 获取基础模型的动态参数表单。 */
const getBaseModelParamsForm = (provider: string, modelType: string, modelName: string) => {
  return get<DynamicFormField[]>(`${prefix}/model_params_form`, {
    model_name: modelName,
    model_type: modelType,
    provider,
  })
}


/** 获取供应商支持的模型类型。 */
const getModelTypeList = (provider: string) => {
  return get<ModelTypeOption[]>(`${prefix}/model_type_list`, { provider })
}

/** 获取供应商指定类型下的基础模型。 */
const getBaseModelList = (provider: string, modelType: string) => {
  return get<BaseModelOption[]>(`${prefix}/model_list`, {
    model_type: modelType,
    provider,
  })
}

export default {
  getBaseModelList,
  getBaseModelParamsForm,
  getModelCreateForm,
  getModelTypeList,
  getProviderList,
  getProviderListByModelType,
}
