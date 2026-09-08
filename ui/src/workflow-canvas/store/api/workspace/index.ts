import { post } from '@/api/admin/core/request'
import modelAPI from '@/api/admin/workspace/model/model'
import providerAPI from '@/api/admin/model-provider'
import toolAPI from '@/api/admin/workspace/tool/tool'
import type { McpTool } from '@/workflow-canvas/store'
import { getWorkspaceId } from '@/utils/resource-context'

/** resourceType: application | tool | knowledge */
const getMcpTools = (resourceType: string, resourceId: string, mcpServers: string) => {
  const workspaceId = getWorkspaceId()
  return post<{ mcp_servers: string }, McpTool[]>(
    `/workspace/${workspaceId}/${resourceType}/${resourceId}/mcp_tools`,
    { mcp_servers: mcpServers },
  )
}

export default {
  getModelList: modelAPI.getModelList,
  getProviderList: providerAPI.getProviderList,
  getModelParamsForm: modelAPI.getModelParamsForm,
  getMcpTools,
  getToolListWithShared: toolAPI.getToolListWithShared,
  getToolById: toolAPI.getToolDetail,
}
