import { del, getExportFile, get, post, put } from '../../core/request'
import type { ParamsPage, ResponsePage } from '../../core/types'
import type {
  RequestParams,
  ToolDebugPayload,
  ToolItem,
  ToolPayload,
  ToolPylintIssue,
} from '@/api/types'
import { getWorkspaceId } from '@/utils/workspace-context'

const getPrefix = () => {
  const workspaceId = getWorkspaceId()
  return `/workspace/${workspaceId}/tool`
}

/** 获取工具分页列表。 */
const getToolPage = (page: ParamsPage, query?: RequestParams) => {
  return get<ResponsePage<ToolItem>>(`${getPrefix()}/${page.currentPage}/${page.pageSize}`, query)
}

/** 删除工作空间工具。 */
const deleteTool = (toolId: string) => {
  return del<undefined, boolean>(`${getPrefix()}/${toolId}`)
}

/** 创建工作空间工具。 */
const postTool = (payload: ToolPayload) => {
  return post<ToolPayload, ToolItem>(getPrefix(), payload)
}

/** 更新工作空间工具。 */
const putTool = (toolId: string, payload: ToolPayload) => {
  return put<ToolPayload, ToolItem>(`${getPrefix()}/${toolId}`, payload)
}

/** 获取工具详情。 */
const getToolDetail = (toolId: string) => {
  return get<ToolItem>(`${getPrefix()}/${toolId}`)
}

/** 导入工具文件并创建工作空间工具。 */
const postToolImport = (file: File, folderId: string) => {
  const payload = new FormData()
  payload.append('file', file)
  payload.append('folder_id', folderId)
  return post<FormData, ToolItem>(`${getPrefix()}/import`, payload)
}

/** 导出工作空间工具文件。 */
const exportTool = (toolId: string, toolName: string) => {
  return getExportFile(`${toolName}.tool`, `${getPrefix()}/${toolId}/export`)
}

/** 检查工作空间工具的 Python 代码。 */
const postToolPylint = (code: string) => {
  return post<{ code: string }, ToolPylintIssue[]>(`${getPrefix()}/pylint`, { code })
}

// const generateCode = (data: any) => {
//   const p = (window.MaxKB?.prefix ? window.MaxKB?.prefix : '/admin') + '/api'
//   return postStream(`${p}${getPrefix()}/generate_code`, data)
// }

/** 调试自定义工具代码并返回运行结果。 */
const postToolDebug = (payload: ToolDebugPayload) => {
  return post<ToolDebugPayload, unknown>(`${getPrefix()}/debug`, payload)
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
  getToolPage,
  exportTool,
  deleteTool,
  getToolDetail,

  postTool,
  postToolDebug,
  postToolImport,
  postToolPylint,
  postToolTestConnection,
  putBatchDeleteTools,
  putBatchMoveTools,
  putTool,
}
