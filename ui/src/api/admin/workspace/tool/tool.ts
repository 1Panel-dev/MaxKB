import { del, get, post, put } from '../../core/request'
import type { ParamsPage, ResponsePage } from '../../core/types'
import type {
  ToolCatalogResponse,
  ToolListQuery,
  ToolPayload,
  ToolTreeResponse,
  WorkspaceTool,
} from '@/api/types'

const getPrefix = (workspaceId: string) => `/workspace/${workspaceId}/tool`

/** 获取工具分页列表。 */
const getToolPage = (workspaceId: string, page: ParamsPage, query?: ToolListQuery) => {
  return get<ResponsePage<WorkspaceTool>>(
    `${getPrefix(workspaceId)}/${page.currentPage}/${page.pageSize}`,
    query,
  )
}

/** 获取当前目录下的工具和子文件夹。 */
const getToolTree = (workspaceId: string, query?: ToolListQuery) => {
  return get<ToolTreeResponse>(getPrefix(workspaceId), query)
}

/** 获取工作空间全部工具以及已授权的共享工具。 */
const getToolCatalog = (workspaceId: string, query?: ToolListQuery) => {
  return get<ToolCatalogResponse>(`${getPrefix(workspaceId)}/tool_list`, query)
}

/** 创建工作空间工具。 */
const postTool = (workspaceId: string, payload: ToolPayload) => {
  return post<ToolPayload, WorkspaceTool>(getPrefix(workspaceId), payload)
}

/** 更新工作空间工具。 */
const putTool = (workspaceId: string, toolId: string, payload: ToolPayload) => {
  return put<ToolPayload, WorkspaceTool>(`${getPrefix(workspaceId)}/${toolId}`, payload)
}

/** 获取工具详情。 */
const getToolDetail = (workspaceId: string, toolId: string) => {
  return get<WorkspaceTool>(`${getPrefix(workspaceId)}/${toolId}`)
}

/** 删除工作空间工具。 */
const deleteTool = (workspaceId: string, toolId: string) => {
  return del<undefined, boolean>(`${getPrefix(workspaceId)}/${toolId}`)
}

/** 测试工具配置是否可连接。 */
const postToolTestConnection = (workspaceId: string, payload: ToolPayload) => {
  return post<ToolPayload, boolean>(`${getPrefix(workspaceId)}/test_connection`, payload)
}

/** 批量删除工作空间工具。 */
const putBatchDeleteTools = (workspaceId: string, toolIds: string[]) => {
  return put<{ id_list: string[] }, boolean>(`${getPrefix(workspaceId)}/batch_delete`, {
    id_list: toolIds,
  })
}

/** 批量移动工作空间工具。 */
const putBatchMoveTools = (workspaceId: string, toolIds: string[], folderId: string) => {
  return put<{ folder_id: string; id_list: string[] }, boolean>(
    `${getPrefix(workspaceId)}/batch_move`,
    { folder_id: folderId, id_list: toolIds },
  )
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
