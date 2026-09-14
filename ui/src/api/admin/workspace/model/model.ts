import { del, get, post, put } from '../../core/request'
import type { Dict, DynamicFormField, ModelPayload, ModelItem } from '@/api/types'
import { getWorkspaceId } from '@/utils/resource-context'

const getPrefix = () => {
  const workspaceId = getWorkspaceId()
  return `/workspace/${workspaceId}/model`
}

/** 获取工作空间模型列表。 */
const getModelList = (query?: Dict<unknown>) => {
  return get<ModelItem[]>(getPrefix(), query)
}

/** 获取包含已授权共享模型的下拉选项。 */
const getModelListWithShared = (query?: Dict<unknown>): Promise<ModelItem[]> => {
  return get<{ shared_model: ModelItem[]; model: ModelItem[] }>(`/workspace/${getWorkspaceId()}/model_list`, query).then(
    ({ shared_model, model }) => [
      ...shared_model.map((model): ModelItem => ({ ...model, source: 'shared' })),
      ...model.map((model): ModelItem => ({ ...model, source: 'workspace' })),
    ],
  )
}

/** 创建工作空间模型。 */
const postModel = (payload: ModelPayload) => {
  return post<ModelPayload, ModelItem>(getPrefix(), payload)
}

/** 更新工作空间模型。 */
const putModel = (modelId: string, payload: Partial<ModelPayload>) => {
  return put<Partial<ModelPayload>, ModelItem>(`${getPrefix()}/${modelId}`, payload)
}

/** 获取包含认证信息的模型详情。 */
const getModelDetail = (modelId: string) => {
  return get<ModelItem>(`${getPrefix()}/${modelId}`)
}

/** 获取不包含认证信息的模型元数据。 */
const getModelMeta = (modelId: string) => {
  return get<ModelItem>(`${getPrefix()}/${modelId}/meta`)
}

/** 删除工作空间模型。 */
const deleteModel = (modelId: string) => {
  return del<undefined, boolean>(`${getPrefix()}/${modelId}`)
}

/** 获取模型参数表单。 */
const getModelParamsForm = (modelId: string) => {
  return get<DynamicFormField[]>(`${getPrefix()}/${modelId}/model_params_form`)
}

/** 保存模型参数表单。 */
const putModelParamsForm = (modelId: string, payload: DynamicFormField[]) => {
  return put<DynamicFormField[], boolean>(`${getPrefix()}/${modelId}/model_params_form`, payload)
}

/** 暂停本地模型下载。 */
const putPauseModelDownload = (modelId: string) => {
  return put<undefined, boolean>(`${getPrefix()}/${modelId}/pause_download`)
}

export default {
  deleteModel,
  getModelDetail,
  getModelList,
  getModelListWithShared,
  getModelMeta,
  getModelParamsForm,
  postModel,
  putModel,
  putModelParamsForm,
  putPauseModelDownload,
}
