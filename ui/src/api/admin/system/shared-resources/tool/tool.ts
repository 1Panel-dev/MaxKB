import { del, downloadRequest, getExportFile, get, post, put } from '../../../core/request'
import type { ParamsPage, ResponsePage } from '../../../core/types'
import type { Dict, ToolDebugPayload, ToolItem, ToolPayload, ToolPylintIssue } from '@/api/types'

const prefix = '/system/shared/tool'

/** 获取当前系统范围可用的工具选项。 */
const getToolListWithShared = (query?: Dict<unknown>) =>
  get<{ tools: ToolItem[]; shared_tools: ToolItem[] }>(`${prefix}/tool_list`, query).then(({ tools, shared_tools }) => [...tools, ...shared_tools])

/** 获取工具分页列表。 */
const getToolPage = (page: ParamsPage, query?: Dict<unknown>) => {
  return get<ResponsePage<ToolItem>>(`${prefix}/${page.currentPage}/${page.pageSize}`, query)
}

/** 删除System 共享工具。 */
const deleteTool = (toolId: string) => {
  return del<undefined, boolean>(`${prefix}/${toolId}`)
}

/** 创建System 共享工具。 */
const postTool = (payload: ToolPayload) => {
  return post<ToolPayload, ToolItem>(prefix, payload)
}

/** 更新System 共享工具。 */
const putTool = (toolId: string, payload: ToolPayload) => {
  return put<ToolPayload, ToolItem>(`${prefix}/${toolId}`, payload)
}

/** 检查System 共享工具的 Python 代码。 */
const postToolPylint = (code: string) => {
  return post<{ code: string }, ToolPylintIssue[]>(`${prefix}/pylint`, { code })
}

/** 调试普通工具代码并返回运行结果。 */
const postToolDebug = (payload: ToolDebugPayload) => {
  return post<ToolDebugPayload, unknown>(`${prefix}/debug`, payload)
}

/** 获取工具详情。 */
const getToolDetail = (toolId: string) => {
  return get<ToolItem>(`${prefix}/${toolId}`)
}

/** 导入工具文件并创建System 共享工具。 */
const postToolImport = (file: File, folderId: string) => {
  const payload = new FormData()
  payload.append('file', file)
  if (folderId) payload.append('folder_id', folderId)
  return post<FormData, ToolItem>(`${prefix}/import`, payload)
}

/** 上传 Skill 压缩包并返回临时文件 ID。 */
const putUploadSkillFile = (file: File) => {
  const payload = new FormData()
  payload.append('file', file)
  return put<FormData, string>(`${prefix}/upload_skill_file`, payload)
}

/** 下载 Skill 工具的压缩包。 */
const downloadSkillFile = (toolId: string) => {
  return downloadRequest(`${prefix}/${toolId}/download_skill_file`, 'GET')
}

/** 导出System 共享工具文件。 */
const exportTool = (toolId: string, toolName: string) => {
  return getExportFile(`${toolName}.tool`, `${prefix}/${toolId}/export`)
}

/** 测试工具配置是否可连接。 */
const postToolTestConnection = (payload: ToolPayload) => {
  return post<ToolPayload, boolean>(`${prefix}/test_connection`, payload)
}

export default {
  getToolListWithShared,
  getToolPage,
  exportTool,
  deleteTool,
  getToolDetail,
  downloadSkillFile,
  postTool,
  postToolDebug,
  postToolImport,
  putUploadSkillFile,
  postToolPylint,
  postToolTestConnection,
  putTool,
}
