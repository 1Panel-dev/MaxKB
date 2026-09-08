import { get, post } from '@/api/admin/core/request'
import type { KnowledgeTagGroup } from '@/api/types'
import modelAPI from '@/api/admin/workspace/model/model'
import providerAPI from '@/api/admin/model-provider'
import toolAPI from '@/api/admin/workspace/tool/tool'
import type { McpTool } from '@/workflow-canvas/store'
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

export default {
  getModelList: modelAPI.getModelList,
  getProviderList: providerAPI.getProviderList,
  getModelParamsForm: modelAPI.getModelParamsForm,
  getMcpTools,
  getToolListWithShared: toolAPI.getToolListWithShared,
  getToolById: toolAPI.getToolDetail,
  getAllTags,
}
