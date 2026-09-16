import { get, put } from '../../core/request'
import type { WorkflowVersion, WorkflowVersionPayload } from '@/api/types'
import { getWorkspaceId } from '@/utils/resource-context'

const getPrefix = (knowledgeId: string) => `/workspace/${getWorkspaceId()}/knowledge/${knowledgeId}/knowledge_version`

/** 获取知识库发布历史，按发布时间倒序返回完整版本快照。 */
const getWorkflowVersions = (knowledgeId: string) => get<WorkflowVersion[]>(getPrefix(knowledgeId))

/** 修改知识库历史版本标题和更新说明，更新说明需要服务端支持 description 字段。 */
const putWorkflowVersion = (knowledgeId: string, versionId: string, data: WorkflowVersionPayload) =>
  put<WorkflowVersionPayload, WorkflowVersion>(`${getPrefix(knowledgeId)}/${versionId}`, data)

export default { getWorkflowVersions, putWorkflowVersion }
