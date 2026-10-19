import { get, put } from '@/api/admin/core/request'
import type { WorkflowVersion, WorkflowVersionPayload } from '@/api/types'

const getPrefix = (applicationId: string) => `/system/resource/application/${applicationId}/application_version`

/** 获取智能体发布历史，按发布时间倒序返回完整版本快照。 */
const getWorkflowVersions = (applicationId: string) => get<WorkflowVersion[]>(getPrefix(applicationId))

/** 修改智能体历史版本标题和更新说明，更新说明需要服务端支持 description 字段。 */
const putWorkflowVersion = (applicationId: string, versionId: string, data: WorkflowVersionPayload) =>
  put<WorkflowVersionPayload, WorkflowVersion>(`${getPrefix(applicationId)}/${versionId}`, data)

export default { getWorkflowVersions, putWorkflowVersion }
