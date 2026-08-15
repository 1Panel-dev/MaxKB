import { del, get, post, put } from '../../core/request'
import type {
  DynamicFormField,
  ModelListQuery,
  ModelPayload,
  SelectableModelResponse,
  WorkspaceModel,
} from '@/api/types'

const getPrefix = (workspaceId: string) => `/workspace/${workspaceId}/model`

/** 获取工作空间模型列表。 */
const getModelList = (workspaceId: string, query?: ModelListQuery) => {
  return get<WorkspaceModel[]>(getPrefix(workspaceId), query)
}

/** 获取工作空间可选模型，并区分工作空间模型与共享模型。 */
const getSelectableModelList = (workspaceId: string, query?: ModelListQuery) => {
  return get<SelectableModelResponse>(`/workspace/${workspaceId}/model_list`, query)
}

/** 获取模型参数表单。 */
const getModelParamsForm = (workspaceId: string, modelId: string) => {
  return get<DynamicFormField[]>(`${getPrefix(workspaceId)}/${modelId}/model_params_form`)
}

/** 创建工作空间模型。 */
const postModel = (workspaceId: string, payload: ModelPayload) => {
  return post<ModelPayload, WorkspaceModel>(getPrefix(workspaceId), payload)
}

/** 更新工作空间模型。 */
const putModel = (workspaceId: string, modelId: string, payload: Partial<ModelPayload>) => {
  return put<Partial<ModelPayload>, WorkspaceModel>(`${getPrefix(workspaceId)}/${modelId}`, payload)
}

/** 保存模型参数配置。 */
const putModelParamsForm = (workspaceId: string, modelId: string, payload: DynamicFormField[]) => {
  return put<DynamicFormField[], WorkspaceModel>(
    `${getPrefix(workspaceId)}/${modelId}/model_params_form`,
    payload,
  )
}

/** 获取包含认证信息的模型详情。 */
const getModelDetail = (workspaceId: string, modelId: string) => {
  return get<WorkspaceModel>(`${getPrefix(workspaceId)}/${modelId}`)
}

/** 获取不包含认证信息的模型元数据。 */
const getModelMeta = (workspaceId: string, modelId: string) => {
  return get<WorkspaceModel>(`${getPrefix(workspaceId)}/${modelId}/meta`)
}

/** 暂停本地模型下载。 */
const putPauseModelDownload = (workspaceId: string, modelId: string) => {
  return put<undefined, boolean>(`${getPrefix(workspaceId)}/${modelId}/pause_download`)
}

/** 删除工作空间模型。 */
const deleteModel = (workspaceId: string, modelId: string) => {
  return del<undefined, boolean>(`${getPrefix(workspaceId)}/${modelId}`)
}

export default {
  deleteModel,
  getModelDetail,
  getModelList,
  getModelMeta,
  getModelParamsForm,
  getSelectableModelList,
  postModel,
  putModel,
  putModelParamsForm,
  putPauseModelDownload,
}
