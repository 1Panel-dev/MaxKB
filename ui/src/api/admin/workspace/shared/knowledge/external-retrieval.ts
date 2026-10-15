import { get } from '../../../core/request'
import type { KnowledgeExternalRetrievalSetting } from '@/api/types'
import { getWorkspaceId } from '@/utils/resource-context'

const getPrefix = (knowledgeId: string) => `/system/shared/workspace/${getWorkspaceId()}/knowledge/${knowledgeId}`

/** 获取知识库外部检索服务配置。 */
const getKnowledgeExternalRetrieval = (knowledgeId: string) => get<KnowledgeExternalRetrievalSetting>(`${getPrefix(knowledgeId)}/external_service`)

export default { getKnowledgeExternalRetrieval }
