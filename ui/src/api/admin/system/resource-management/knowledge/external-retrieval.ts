import { get, put } from '@/api/admin/core/request'
import type { KnowledgeExternalRetrievalPayload, KnowledgeExternalRetrievalSetting } from '@/api/types'

const getPrefix = (knowledgeId: string) => `/system/resource/knowledge/${knowledgeId}`

/** 获取知识库外部检索服务配置。 */
const getKnowledgeExternalRetrieval = (knowledgeId: string) => get<KnowledgeExternalRetrievalSetting>(`${getPrefix(knowledgeId)}/external_service`)

/** 保存知识库外部检索服务开关。 */
const putKnowledgeExternalRetrieval = (knowledgeId: string, payload: KnowledgeExternalRetrievalPayload) =>
  put<KnowledgeExternalRetrievalPayload, KnowledgeExternalRetrievalSetting>(`${getPrefix(knowledgeId)}/external_service`, payload)

export default { getKnowledgeExternalRetrieval, putKnowledgeExternalRetrieval }
