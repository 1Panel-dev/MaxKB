import { del, get, post, put } from '../../core/request'
import type { RequestParams, WorkspaceModel } from '@/api/types'

const getPrefix = (workspaceId: string) => `/system/shared/workspace/${workspaceId}`

/** 获取工作空间共享的模型列表。 */
const getModelList = (workspaceId: string, query?: RequestParams) => {
  return get<WorkspaceModel[]>(`${getPrefix(workspaceId)}/model`, query)
}

export default {
  getModelList,
}
