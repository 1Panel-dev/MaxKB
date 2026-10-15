import { del, get, post, put } from '@/api/admin/core/request'
import type { ParamsPage, ResponsePage } from '@/api/admin/core/types'
import type { ParagraphProblem, ProblemBatchAssociationPayload, ProblemParagraph } from '@/api/types'

const getPrefix = (knowledgeId: string) => `/system/resource/knowledge/${knowledgeId}/problem`

/** 批量创建知识库问题。 */
const postProblems = (knowledgeId: string, contents: string[]) => post<string[], void>(getPrefix(knowledgeId), contents)

/** 分页搜索知识库问题，供分段选择已有问题进行关联。 */
const getProblemsPage = (knowledgeId: string, page: ParamsPage, query?: { content?: string }) =>
  get<ResponsePage<ParagraphProblem>>(`${getPrefix(knowledgeId)}/${page.currentPage}/${page.pageSize}`, query)

/** 编辑单个知识库问题的内容。 */
const putProblem = (knowledgeId: string, problemId: string, content: string) =>
  put<{ content: string }, void>(`${getPrefix(knowledgeId)}/${problemId}`, { content })

/** 删除单个知识库问题。 */
const deleteProblem = (knowledgeId: string, problemId: string) => del<undefined, boolean>(`${getPrefix(knowledgeId)}/${problemId}`)

/** 获取问题当前关联的文档分段。 */
const getProblemParagraphs = (knowledgeId: string, problemId: string) => get<ProblemParagraph[]>(`${getPrefix(knowledgeId)}/${problemId}/paragraph`)

/** 批量将问题关联到指定文档分段。 */
const putBatchAssociateProblems = (knowledgeId: string, payload: ProblemBatchAssociationPayload) =>
  put<ProblemBatchAssociationPayload, boolean>(`${getPrefix(knowledgeId)}/batch_association`, payload)

/** 批量删除知识库问题。 */
const putBatchDeleteProblems = (knowledgeId: string, problemIds: string[]) =>
  put<string[], boolean>(`${getPrefix(knowledgeId)}/batch_delete`, problemIds)

export default {
  postProblems,
  getProblemsPage,
  putProblem,
  deleteProblem,
  getProblemParagraphs,
  putBatchAssociateProblems,
  putBatchDeleteProblems,
}
