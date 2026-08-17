import { del, get, post, put } from '../../core/request'
import type { RequestParams, ModelPayload, WorkspaceModel } from '@/api/types'

const getPrefix = (workspaceId: string) => `/workspace/${workspaceId}/model`

/** 获取工作空间模型列表。 */
const getModelList = (workspaceId: string, query?: RequestParams) => {
  return get<WorkspaceModel[]>(getPrefix(workspaceId), query)
}

/** 创建工作空间模型。 */
const postModel = (workspaceId: string, payload: ModelPayload) => {
  return post<ModelPayload, WorkspaceModel>(getPrefix(workspaceId), payload)
}

/** 更新工作空间模型。 */
const putModel = (workspaceId: string, modelId: string, payload: Partial<ModelPayload>) => {
  return put<Partial<ModelPayload>, WorkspaceModel>(`${getPrefix(workspaceId)}/${modelId}`, payload)
}

/** 获取包含认证信息的模型详情。 */
const getModelDetail = (workspaceId: string, modelId: string) => {
  return get<WorkspaceModel>(`${getPrefix(workspaceId)}/${modelId}`)
}

/** 获取不包含认证信息的模型元数据。 */
const getModelMeta = (workspaceId: string, modelId: string) => {
  return get<WorkspaceModel>(`${getPrefix(workspaceId)}/${modelId}/meta`)
}

/** 删除工作空间模型。 */
const deleteModel = (workspaceId: string, modelId: string) => {
  return del<undefined, boolean>(`${getPrefix(workspaceId)}/${modelId}`)
}

/** 暂停本地模型下载。 */
const putPauseModelDownload = (workspaceId: string, modelId: string) => {
  return put<undefined, boolean>(`${getPrefix(workspaceId)}/${modelId}/pause_download`)
}

export default {
  deleteModel,
  getModelDetail,
  getModelList,
  getModelMeta,
  postModel,
  putModel,
  putPauseModelDownload,
}
