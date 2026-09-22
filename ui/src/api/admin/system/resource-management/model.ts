import { del, get, post, put } from '../../core/request'
import type { ParamsPage, ResponsePage } from '../../core/types'
import type { Dict, DynamicFormField, ModelItem, ModelPayload } from '@/api/types'

const prefix = '/system/resource/model'

/** 获取跨工作空间的模型分页列表。 */
const getModelPage = (page: ParamsPage, query?: Dict<unknown>) =>
  get<ResponsePage<ModelItem>>(`${prefix}/${page.currentPage}/${page.pageSize}`, query)

/** 获取系统资源范围的模型及共享模型选项。 */
const getModelListWithShared = (query?: Dict<unknown>): Promise<ModelItem[]> =>
  get<{ shared_model: ModelItem[]; model: ModelItem[] }>(`${prefix}/model_list`, query).then(({ shared_model, model }) => [
    ...shared_model.map((model): ModelItem => ({ ...model, source: 'shared' })),
    ...model.map((model): ModelItem => ({ ...model, source: 'workspace' })),
  ])

/** 获取包含认证信息的模型详情。 */
const getModelDetail = (modelId: string) => get<ModelItem>(`${prefix}/${modelId}`)

/** 创建系统资源模型。 */
const postModel = (payload: ModelPayload) => post<ModelPayload, ModelItem>(prefix, payload)

/** 更新模型配置。 */
const putModel = (modelId: string, payload: Partial<ModelPayload>) => put<Partial<ModelPayload>, ModelItem>(`${prefix}/${modelId}`, payload)

/** 删除模型。 */
const deleteModel = (modelId: string) => del<undefined, boolean>(`${prefix}/${modelId}`)

/** 获取模型参数表单。 */
const getModelParamsForm = (modelId: string) => get<DynamicFormField[]>(`${prefix}/${modelId}/model_params_form`)

/** 保存模型参数表单。 */
const putModelParamsForm = (modelId: string, payload: DynamicFormField[]) =>
  put<DynamicFormField[], boolean>(`${prefix}/${modelId}/model_params_form`, payload)

export default { getModelPage, getModelListWithShared, getModelDetail, postModel, putModel, deleteModel, getModelParamsForm, putModelParamsForm }
