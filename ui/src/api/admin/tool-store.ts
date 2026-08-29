import { get, post } from './core/request'
import type { Dict, ToolItem, ToolStoreResponse } from '@/api/types'

/** 获取系统内置工具。 */
const getInternalToolList = (query?: Dict<unknown>) => {
  return get<ToolItem[]>('/workspace/internal/tool', query)
}

/** 获取工具商店列表。 */
const getStoreToolList = (query?: Dict<unknown>) => {
  return get<ToolStoreResponse>('/workspace/store/tool', query)
}

/** 获取知识库模板商店列表。 */
const getStoreKnowledgeList = (query?: Dict<unknown>) => {
  return get<unknown>('/workspace/store/knowledge_template', query)
}

/** 获取工作流工具模板商店列表。 */
const getStoreToolWorkflowList = (query?: Dict<unknown>) => {
  return get<unknown>('/workspace/store/tool_workflow_template', query)
}

/** 获取应用模板商店列表。 */
const getStoreApplicationList = (query?: Dict<unknown>) => {
  return get<unknown>('/workspace/store/application_template', query)
}

export default {
  getInternalToolList,
  getStoreApplicationList,
  getStoreKnowledgeList,
  getStoreToolList,
  getStoreToolWorkflowList,
}
