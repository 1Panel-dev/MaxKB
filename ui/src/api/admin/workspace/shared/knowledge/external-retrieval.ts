import { get, put } from '../../../core/request'
import type { KnowledgeExternalRetrievalPayload, KnowledgeExternalRetrievalSetting } from '@/api/types'
import { getWorkspaceId } from '@/utils/resource-context'

const getPrefix = (knowledgeId: string) => `/system/shared/workspace/${getWorkspaceId()}/knowledge/${knowledgeId}`

/** 获取知识库外部检索服务配置。 */
// TODO：联调确认响应包含 enabled、authentication、api_url、api_example、mcp_url、mcp_config。
// api_example 为后台生成的完整示例文本（string），前端直接展示和复制，不拼接请求内容。
const getKnowledgeExternalRetrieval = (knowledgeId: string) => get<KnowledgeExternalRetrievalSetting>(`${getPrefix(knowledgeId)}/external_service`)

/** 保存知识库外部检索服务开关。 */
// TODO：只更新 payload 中的开关，保留未提交字段，并返回包含最新 api_example 的完整配置。
const putKnowledgeExternalRetrieval = (knowledgeId: string, payload: KnowledgeExternalRetrievalPayload) =>
  put<KnowledgeExternalRetrievalPayload, KnowledgeExternalRetrievalSetting>(`${getPrefix(knowledgeId)}/external_service`, payload)

export default { getKnowledgeExternalRetrieval, putKnowledgeExternalRetrieval }
