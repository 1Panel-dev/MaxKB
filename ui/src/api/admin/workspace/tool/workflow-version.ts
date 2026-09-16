import { get, put } from '../../core/request'
import type { WorkflowVersion, WorkflowVersionPayload } from '@/api/types'
import { getWorkspaceId } from '@/utils/resource-context'

const getPrefix = (toolId: string) => `/workspace/${getWorkspaceId()}/tool/${toolId}/tool_version`

/** 获取工具发布历史，按发布时间倒序返回完整版本快照。 */
const getWorkflowVersions = (toolId: string) => get<WorkflowVersion[]>(getPrefix(toolId))

/** 修改工具历史版本标题和更新说明，更新说明需要服务端支持 description 字段。 */
const putWorkflowVersion = (toolId: string, versionId: string, data: WorkflowVersionPayload) =>
  put<WorkflowVersionPayload, WorkflowVersion>(`${getPrefix(toolId)}/${versionId}`, data)

export default { getWorkflowVersions, putWorkflowVersion }
