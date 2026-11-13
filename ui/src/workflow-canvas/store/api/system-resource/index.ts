import ApplicationApi from '@/api/admin/system/resource-management/application/application'
import { get, post } from '@/api/admin/core/request'
import type { KnowledgeTagGroup } from '@/api/types'
import type { McpTool } from '@/workflow-canvas/store'
import ModelApi from '@/api/admin/system/resource-management/model'
import ToolApi from '@/api/admin/system/resource-management/tool/tool'
import ProviderApi from '@/api/admin/model-provider'
import KnowledgeWorkflowApi from '@/api/admin/system/resource-management/knowledge/workflow'

/** 查询当前系统范围的 MCP 服务工具定义。 */
const getMcpTools = (resourceType: string, resourceId: string, mcpServers: string) =>
  post<{ mcp_servers: string }, McpTool[]>(`/system/resource/${resourceType}/${resourceId}/mcp_tools`, { mcp_servers: mcpServers })

/** 查询当前系统范围内所选知识库的文档标签。 */
const getAllTags = (knowledgeIds: string[]) => get<KnowledgeTagGroup[]>('/system/resource/knowledge/tags', { 'knowledge_ids[]': knowledgeIds })

/** 知识库工作流最近一次执行（调试或导入）的详情，供 AI 生成排查运行报错。 */
const getLatestKnowledgeAction = async (knowledgeId: string) => {
  const page = await KnowledgeWorkflowApi.getKnowledgeExecutionRecordPage(knowledgeId, { currentPage: 1, pageSize: 1 })
  const record = page.records[0]
  return record ? KnowledgeWorkflowApi.getKnowledgeWorkflowAction(knowledgeId, record.id) : null
}

export default {
  getLatestKnowledgeAction,
  getAllApplication: ApplicationApi.getAllApplication,
  postPromptGenerate: ModelApi.postPromptGenerate,
  postChatCompletion: ModelApi.postChatCompletion,
  getMcpTools,
  getAllTags,
  getModelListWithShared: ModelApi.getModelListWithShared,
  getProviderList: ProviderApi.getProviderList,
  getModelParamsForm: ModelApi.getModelParamsForm,
  getToolListWithShared: ToolApi.getToolListWithShared,
  getToolById: ToolApi.getToolDetail,
}
