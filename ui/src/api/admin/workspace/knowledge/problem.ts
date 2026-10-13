import { get } from '../../core/request'
import type { ParamsPage, ResponsePage } from '../../core/types'
import type { ParagraphProblem } from '@/api/types'
import { getWorkspaceId } from '@/utils/resource-context'

/** 分页搜索知识库问题，供分段选择已有问题进行关联。 */
const getProblemsPage = (knowledgeId: string, page: ParamsPage, query?: { content?: string }) =>
  get<ResponsePage<ParagraphProblem>>(`/workspace/${getWorkspaceId()}/knowledge/${knowledgeId}/problem/${page.currentPage}/${page.pageSize}`, query)

export default { getProblemsPage }
