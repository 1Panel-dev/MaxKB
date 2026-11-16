import type { KnowledgeTagGroup } from '@/api/types'
import type { McpTool } from '@/workflow-canvas/store'
import { get, post } from '@/api/admin/core/request'
import providerAPI from '@/api/admin/model-provider'
import ApplicationApi from '@/api/admin/workspace/application/application'
import KnowledgeWorkflowApi from '@/api/admin/workspace/knowledge/workflow'
import modelAPI from '@/api/admin/workspace/model'
import toolAPI from '@/api/admin/workspace/tool/tool'
import { getWorkspaceId } from '@/utils/resource-context'

/** 获取 MCP 调用节点所需的 MCP 工具。 */
/** resourceType: application | tool | knowledge */
const getMcpTools = (resourceType: string, resourceId: string, mcpServers: string) => {
  const workspaceId = getWorkspaceId()
  return post<{ mcp_servers: string }, McpTool[]>(`/workspace/${workspaceId}/${resourceType}/${resourceId}/mcp_tools`, { mcp_servers: mcpServers })
}

/** 获取 文档检索节点所选知识库的全部文档标签。 */
const getAllTags = (knowledgeIds: string[]) => {
  const workspaceId = getWorkspaceId()
  return get<KnowledgeTagGroup[]>(`/workspace/${workspaceId}/knowledge/tags`, { 'knowledge_ids[]': knowledgeIds })
}

/** 知识库工作流最近一次执行（调试或导入）的详情，供 AI 生成排查运行报错。 */
const getLatestKnowledgeAction = async (knowledgeId: string) => {
  const page = await KnowledgeWorkflowApi.getKnowledgeExecutionRecordPage(knowledgeId, { currentPage: 1, pageSize: 1 })
  const record = page.records[0]
  return record ? KnowledgeWorkflowApi.getKnowledgeWorkflowAction(knowledgeId, record.id) : null
}

export default {
  getLatestKnowledgeAction,
  getAllApplication: ApplicationApi.getAllApplication,
  getApplicationDetail: ApplicationApi.getApplicationDetail,
  postPromptGenerate: modelAPI.postPromptGenerate,
  postChatCompletion: modelAPI.postChatCompletion,
  getModelListWithShared: modelAPI.getModelListWithShared,
  getProviderList: providerAPI.getProviderList,
  getModelParamsForm: modelAPI.getModelParamsForm,
  getMcpTools,
  getToolListWithShared: toolAPI.getToolListWithShared,
  getToolById: toolAPI.getToolDetail,
  getAllTags,
}
