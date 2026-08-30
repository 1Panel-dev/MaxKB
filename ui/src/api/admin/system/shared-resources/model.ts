import { del, get, post, put } from '../../core/request'
import type { Dict, DynamicFormField, ModelItem, ModelPayload } from '@/api/types'

const prefix = '/system/shared/model'

/**
 * 获得模型列表
 * @params 参数 name, model_type, model_name
 */
const getModelList = (query?: Dict<unknown>) => {
  return get<ModelItem[]>(prefix, query)
}

/** 创建 System 共享模型。 */
const postModel = (payload: ModelPayload) => {
  return post<ModelPayload, ModelItem>(prefix, payload)
}

/** 获取包含认证信息的 System 共享模型详情。 */
const getModelDetail = (modelId: string) => {
  return get<ModelItem>(`${prefix}/${modelId}`)
}

/** 更新 System 共享模型。 */
const putModel = (modelId: string, payload: Partial<ModelPayload>) => {
  return put<Partial<ModelPayload>, ModelItem>(`${prefix}/${modelId}`, payload)
}

/** 删除 System 共享模型。 */
const deleteModel = (modelId: string) => {
  return del<undefined, boolean>(`${prefix}/${modelId}`)
}

/** 获取 System 共享模型参数表单。 */
const getModelParamsForm = (modelId: string) => {
  return get<DynamicFormField[]>(`${prefix}/${modelId}/model_params_form`)
}

/** 保存 System 共享模型参数表单。 */
const putModelParamsForm = (modelId: string, payload: DynamicFormField[]) => {
  return put<DynamicFormField[], boolean>(`${prefix}/${modelId}/model_params_form`, payload)
}

/** 获取不包含认证信息的 System 共享模型元数据。 */
const getModelMeta = (modelId: string) => {
  return get<ModelItem>(`${prefix}/${modelId}/meta`)
}

/** 暂停 System 共享本地模型下载。 */
const putPauseModelDownload = (modelId: string) => {
  return put<undefined, boolean>(`${prefix}/${modelId}/pause_download`)
}

export default { deleteModel, getModelDetail, getModelList, getModelMeta, getModelParamsForm, postModel, putModel, putModelParamsForm, putPauseModelDownload }
