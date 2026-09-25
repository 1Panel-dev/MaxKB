import { get } from '../../core/request'
import type { ParamsPage, ResponsePage } from '../../core/types'
import type { Dict, ToolItem } from '@/api/types'
import { getWorkspaceId } from '@/utils/resource-context'

const getPrefix = () => `/system/shared/workspace/${getWorkspaceId()}/tool`

/** 获取工作空间共享的分页工具列表。 */
const getToolPage = (page: ParamsPage, query?: Dict<unknown>) => {
  return get<ResponsePage<ToolItem>>(`${getPrefix()}/${page.currentPage}/${page.pageSize}`, query)
}

/** 获取工作空间共享的不分页工具列表。 */
const getAllTool = (query?: Dict<unknown>) => {
  return get<ToolItem[]>(getPrefix(), query)
}

export default { getToolPage, getAllTool }
