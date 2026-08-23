import { get } from '../core/request'
import type { ParamsPage, ResponsePage } from '../core/types'
import type { RequestParams, ModelItem, ToolItem } from '@/api/types'
import { getWorkspaceId } from '@/utils/workspace-context'

const getPrefix = () => {
  const workspaceId = getWorkspaceId()
  return `/system/shared/workspace/${workspaceId}`
}

/** 获取工作空间共享的模型列表。 */
const getModelList = (query?: RequestParams) => {
  return get<ModelItem[]>(`${getPrefix()}/model`, query)
}

/** 获取工作空间共享的工具列表。 */
const getToolPage = (page: ParamsPage, query?: RequestParams) => {
  return get<ResponsePage<ToolItem>>(`${getPrefix()}/tool/${page.currentPage}/${page.pageSize}`, query)
}

export default {
  getModelList,
  getToolPage,
}
