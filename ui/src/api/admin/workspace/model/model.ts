import { del, get, post, put } from '../../core/request'
import type { Dict, ModelPayload, ModelItem } from '@/api/types'
import { getWorkspaceId } from '@/utils/workspace-context'

const getPrefix = () => {
  const workspaceId = getWorkspaceId()
  return `/workspace/${workspaceId}/model`
}

/** 获取工作空间模型列表。 */
const getModelList = (query?: Dict<unknown>) => {
  return get<ModelItem[]>(getPrefix(), query)
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
const getModelParamsForm = (modelId: string) => {
  return get<ModelItem>(`${getPrefix()}/${modelId}/model_params_form`)
}

/** 暂停本地模型下载。 */
const putPauseModelDownload = (modelId: string) => {
  return put<undefined, boolean>(`${getPrefix()}/${modelId}/pause_download`)
}

export default {
  deleteModel,
  getModelDetail,
  getModelList,
  getModelMeta,
  postModel,
  putModel,
  putPauseModelDownload,
  getModelParamsForm,
}
