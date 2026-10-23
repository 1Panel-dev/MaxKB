import { get } from '../../../core/request'
import type { ParamsPage, ResponsePage } from '../../../core/types'
import type { Dict, ProblemItem } from '@/api/types'
import { getWorkspaceId } from '@/utils/resource-context'

const getPrefix = (knowledgeId: string) => `/system/shared/workspace/${getWorkspaceId()}/knowledge/${knowledgeId}/problem`

/** 分页查询工作空间共享知识库的问题，只提供只读访问。 */
const getProblemsPage = (knowledgeId: string, page: ParamsPage, query?: Dict<unknown>) =>
  get<ResponsePage<ProblemItem>>(`${getPrefix(knowledgeId)}/${page.currentPage}/${page.pageSize}`, query)

export default { getProblemsPage }
