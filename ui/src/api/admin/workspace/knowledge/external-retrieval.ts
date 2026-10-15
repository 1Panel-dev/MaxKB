import { get, put } from '../../core/request'
import type { KnowledgeExternalRetrievalPayload, KnowledgeExternalRetrievalSetting } from '@/api/types'
import { getWorkspaceId } from '@/utils/resource-context'

const getPrefix = (knowledgeId: string) => `/workspace/${getWorkspaceId()}/knowledge/${knowledgeId}`

/** 获取知识库外部检索服务配置。 */
const getKnowledgeExternalRetrieval = (knowledgeId: string) => get<KnowledgeExternalRetrievalSetting>(`${getPrefix(knowledgeId)}/external_service`)

/** 保存知识库外部检索服务开关。 */
const putKnowledgeExternalRetrieval = (knowledgeId: string, payload: KnowledgeExternalRetrievalPayload) =>
  put<KnowledgeExternalRetrievalPayload, KnowledgeExternalRetrievalSetting>(`${getPrefix(knowledgeId)}/external_service`, payload)

export default { getKnowledgeExternalRetrieval, putKnowledgeExternalRetrieval }
