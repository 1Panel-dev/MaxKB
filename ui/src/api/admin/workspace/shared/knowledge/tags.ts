import { get } from '../../../core/request'
import type { KnowledgeTagGroup } from '@/api/types'
import { getWorkspaceId } from '@/utils/resource-context'

const getPrefix = (knowledgeId: string) => `/system/shared/workspace/${getWorkspaceId()}/knowledge/${knowledgeId}/tags`

/** 获取工作空间共享知识库按标签名称分组的标签选项。 */
const getKnowledgeTags = (knowledgeId: string) => get<KnowledgeTagGroup[]>(getPrefix(knowledgeId))

export default { getKnowledgeTags }
