import type { Dict } from './common'

/** 知识库外部检索服务配置。 */
export interface KnowledgeExternalRetrievalSetting {
  enabled: boolean
  authentication: boolean
  api_url: string
  api_example: string
  mcp_url: string
  mcp_config: Dict<unknown>
}

/** 每次只提交发生变化的开关，保留其他配置。 */
export interface KnowledgeExternalRetrievalPayload {
  enabled?: boolean
  authentication?: boolean
}
