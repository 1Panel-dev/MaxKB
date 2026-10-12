import { get } from '../../../core/request'
import type { ParamsPage, ResponsePage } from '../../../core/types'
import type { Dict, KnowledgeDetail, KnowledgeItem } from '@/api/types'
import { getWorkspaceId } from '@/utils/resource-context'

const getPrefix = () => `/system/shared/workspace/${getWorkspaceId()}/knowledge`

/** 获取工作空间共享的知识库分页列表。 */
const getKnowledgePage = (page: ParamsPage, query?: Dict<unknown>) =>
  get<ResponsePage<KnowledgeItem>>(`${getPrefix()}/${page.currentPage}/${page.pageSize}`, query)

/** 获取工作空间共享的不分页知识库列表。 */
const getAllKnowledge = (query?: Dict<unknown>) => get<KnowledgeItem[]>(getPrefix(), query)

/** 获取工作空间共享的知识库详情。 */
const getKnowledgeDetail = (knowledgeId: string) => get<KnowledgeDetail>(`${getPrefix()}/${knowledgeId}`)

export default { getKnowledgePage, getAllKnowledge, getKnowledgeDetail }
