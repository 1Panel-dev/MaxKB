import { del, get, post, put } from '../../core/request'
import type { ParamsPage, ResponsePage } from '../../core/types'
import type {
  ToolCatalogResponse,
  ToolListQuery,
  ToolPayload,
  ToolTreeResponse,
  WorkspaceTool,
} from '@/api/types'
import { getWorkspaceId } from '@/utils/workspace-context'

const getPrefix = () => {
  const workspaceId = getWorkspaceId()
  return `/workspace/${workspaceId}/tool`
}

/** 获取工具分页列表。 */
const getToolPage = (page: ParamsPage, query?: ToolListQuery) => {
  return get<ResponsePage<WorkspaceTool>>(
    `${getPrefix()}/${page.currentPage}/${page.pageSize}`,
    query,
  )
}

/** 获取当前目录下的工具和子文件夹。 */
const getToolTree = (query?: ToolListQuery) => {
  return get<ToolTreeResponse>(getPrefix(), query)
}

/** 获取工作空间全部工具以及已授权的共享工具。 */
const getToolCatalog = (query?: ToolListQuery) => {
  return get<ToolCatalogResponse>(`${getPrefix()}/tool_list`, query)
}

/** 创建工作空间工具。 */
const postTool = (payload: ToolPayload) => {
  return post<ToolPayload, WorkspaceTool>(getPrefix(), payload)
}

/** 更新工作空间工具。 */
const putTool = (toolId: string, payload: ToolPayload) => {
  return put<ToolPayload, WorkspaceTool>(`${getPrefix()}/${toolId}`, payload)
}

/** 获取工具详情。 */
const getToolDetail = (toolId: string) => {
  return get<WorkspaceTool>(`${getPrefix()}/${toolId}`)
}

/** 删除工作空间工具。 */
const deleteTool = (toolId: string) => {
  return del<undefined, boolean>(`${getPrefix()}/${toolId}`)
}

/** 测试工具配置是否可连接。 */
const postToolTestConnection = (payload: ToolPayload) => {
  return post<ToolPayload, boolean>(`${getPrefix()}/test_connection`, payload)
}

/** 批量删除工作空间工具。 */
const putBatchDeleteTools = (toolIds: string[]) => {
  return put<{ id_list: string[] }, boolean>(`${getPrefix()}/batch_delete`, {
    id_list: toolIds,
  })
}

/** 批量移动工作空间工具。 */
const putBatchMoveTools = (toolIds: string[], folderId: string) => {
  return put<{ folder_id: string; id_list: string[] }, boolean>(`${getPrefix()}/batch_move`, {
    folder_id: folderId,
    id_list: toolIds,
  })
}

export default {
  deleteTool,
  getToolCatalog,
  getToolDetail,
  getToolPage,
  getToolTree,
  postTool,
  postToolTestConnection,
  putBatchDeleteTools,
  putBatchMoveTools,
  putTool,
}
