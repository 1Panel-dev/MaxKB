import { get, post } from '@/api/admin/core/request'
import type { KnowledgeTagGroup } from '@/api/types'
import type { McpTool } from '@/workflow-canvas/store'
import ApplicationApi from '@/api/admin/system/resource-management/application/application'
import ModelApi from '@/api/admin/system/resource-management/model'
import ToolApi from '@/api/admin/system/resource-management/tool/tool'
import ProviderApi from '@/api/admin/model-provider'

/** 查询当前系统范围的 MCP 服务工具定义。 */
const getMcpTools = (resourceType: string, resourceId: string, mcpServers: string) =>
  post<{ mcp_servers: string }, McpTool[]>(`/system/resource/${resourceType}/${resourceId}/mcp_tools`, { mcp_servers: mcpServers })

/** 查询当前系统范围内所选知识库的文档标签。 */
const getAllTags = (knowledgeIds: string[]) => get<KnowledgeTagGroup[]>('/system/resource/knowledge/tags', { 'knowledge_ids[]': knowledgeIds })

export default {
  postPromptGenerate: ApplicationApi.postPromptGenerate,
  getMcpTools,
  getAllTags,
  getModelListWithShared: ModelApi.getModelListWithShared,
  getProviderList: ProviderApi.getProviderList,
  getModelParamsForm: ModelApi.getModelParamsForm,
  getToolListWithShared: ToolApi.getToolListWithShared,
  getToolById: ToolApi.getToolDetail,
}
