import { get, post } from '../../core/request'
import type { AddStoreToolPayload, WorkspaceTool } from '@/api/types'
import type { RequestParams } from '@/api/types'

/** 获取系统内置工具。 */
const getInternalToolList = (query?: RequestParams) => {
  return get<WorkspaceTool[]>('/workspace/internal/tool', query)
}

/** 获取工具商店列表。 */
const getStoreToolList = (query?: RequestParams) => {
  return get<unknown>('/workspace/store/tool', query)
}

/** 获取知识库模板商店列表。 */
const getStoreKnowledgeList = (query?: RequestParams) => {
  return get<unknown>('/workspace/store/knowledge_template', query)
}

/** 获取工作流工具模板商店列表。 */
const getStoreToolWorkflowList = (query?: RequestParams) => {
  return get<unknown>('/workspace/store/tool_workflow_template', query)
}

/** 获取应用模板商店列表。 */
const getStoreApplicationList = (query?: RequestParams) => {
  return get<unknown>('/workspace/store/application_template', query)
}

/** 将系统内置工具添加到工作空间。 */
const postInternalTool = (workspaceId: string, toolId: string, payload: AddStoreToolPayload) => {
  return post<AddStoreToolPayload, WorkspaceTool>(
    `/workspace/${workspaceId}/tool/${toolId}/add_internal_tool`,
    payload,
  )
}

/** 将商店工具添加到工作空间。 */
const postStoreTool = (workspaceId: string, toolId: string, payload: AddStoreToolPayload) => {
  return post<AddStoreToolPayload, WorkspaceTool>(
    `/workspace/${workspaceId}/tool/${toolId}/add_store_tool`,
    payload,
  )
}

export default {
  getInternalToolList,
  getStoreApplicationList,
  getStoreKnowledgeList,
  getStoreToolList,
  getStoreToolWorkflowList,
  postInternalTool,
  postStoreTool,
}
