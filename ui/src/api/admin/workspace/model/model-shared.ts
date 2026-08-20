import { get } from '../../core/request'
import type { RequestParams, WorkspaceModel } from '@/api/types'
import { getWorkspaceId } from '@/utils/workspace-context'

const getPrefix = () => {
  const workspaceId = getWorkspaceId()
  return `/system/shared/workspace/${workspaceId}`
}

/** 获取工作空间共享的模型列表。 */
const getModelList = (query?: RequestParams) => {
  return get<WorkspaceModel[]>(`${getPrefix()}/model`, query)
}

export default {
  getModelList,
}
