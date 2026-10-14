import { del, get, post, put } from '../../core/request'
import type { ParamsPage, ResponsePage } from '../../core/types'
import type {
  ParagraphCreatePayload,
  ParagraphDetail,
  ParagraphEditPayload,
  ParagraphGeneratePayload,
  ParagraphItem,
  ParagraphProblem,
  ParagraphQuery,
} from '@/api/types'
import { getWorkspaceId } from '@/utils/resource-context'

const getPrefix = (knowledgeId: string, documentId: string) =>
  `/workspace/${getWorkspaceId()}/knowledge/${knowledgeId}/document/${documentId}/paragraph`

/** 分页查询文档分段，供详情页滚动加载。 */
const getParagraphPage = (knowledgeId: string, documentId: string, page: ParamsPage, query?: ParagraphQuery) =>
  get<ResponsePage<ParagraphItem>>(`${getPrefix(knowledgeId, documentId)}/${page.currentPage}/${page.pageSize}`, { ...query })

/** 在指定位置新增分段，默认首位，由服务端触发索引。 */
const postParagraph = (knowledgeId: string, documentId: string, payload: ParagraphCreatePayload) =>
  post<ParagraphCreatePayload, ParagraphDetail>(getPrefix(knowledgeId, documentId), payload)

/** 查询分段正文、召回统计及关联问题。 */
const getParagraphDetail = (knowledgeId: string, documentId: string, paragraphId: string) =>
  get<ParagraphDetail>(`${getPrefix(knowledgeId, documentId)}/${paragraphId}`)

/** 更新分段正文或启用状态，返回最新详情。 */
const putParagraph = (knowledgeId: string, documentId: string, paragraphId: string, payload: ParagraphEditPayload) =>
  put<ParagraphEditPayload, ParagraphDetail>(`${getPrefix(knowledgeId, documentId)}/${paragraphId}`, payload)

/** 新增问题并关联到当前分段。 */
const postParagraphProblem = (knowledgeId: string, documentId: string, paragraphId: string, content: string) =>
  post<{ content: string }, ParagraphProblem>(`${getPrefix(knowledgeId, documentId)}/${paragraphId}/problem`, { content })

/** 获取当前分段关联的全部问题。 */
const getParagraphProblems = (knowledgeId: string, documentId: string, paragraphId: string) =>
  get<ParagraphProblem[]>(`${getPrefix(knowledgeId, documentId)}/${paragraphId}/problem`)

/** 将知识库中的已有问题关联到当前分段。 */
const putAssociateParagraphProblem = (knowledgeId: string, documentId: string, paragraphId: string, problemId: string) =>
  put<undefined, boolean>(`${getPrefix(knowledgeId, documentId)}/association`, undefined, { paragraph_id: paragraphId, problem_id: problemId })

/** 解除当前分段的问题关联，保留问题及其他分段的关联。 */
const putUnassociateParagraphProblem = (knowledgeId: string, documentId: string, paragraphId: string, problemId: string) =>
  put<undefined, boolean>(`${getPrefix(knowledgeId, documentId)}/unassociation`, undefined, { paragraph_id: paragraphId, problem_id: problemId })

/** 批量/单个将所选分段批量迁移至目标知识库的文档。 */
const putMigrateParagraphs = (knowledgeId: string, documentId: string, targetKnowledgeId: string, targetDocumentId: string, paragraphIds: string[]) =>
  put<{ id_list: string[] }, boolean>(`${getPrefix(knowledgeId, documentId)}/migrate/knowledge/${targetKnowledgeId}/document/${targetDocumentId}`, {
    id_list: paragraphIds,
  })

/** 批量/单个为生成问题。 */
const putGenerateParagraphQuestions = (knowledgeId: string, documentId: string, payload: ParagraphGeneratePayload) =>
  put<ParagraphGeneratePayload, void>(`${getPrefix(knowledgeId, documentId)}/batch_generate_related`, payload)

/** 批量删除当前文档中所选的分段。 */
const putBatchDeleteParagraphs = (knowledgeId: string, documentId: string, paragraphIds: string[]) =>
  put<{ id_list: string[] }, boolean>(`${getPrefix(knowledgeId, documentId)}/batch_delete`, { id_list: paragraphIds })

/** 删除当前文档的单个分段及其关联数据。 */
const deleteParagraph = (knowledgeId: string, documentId: string, paragraphId: string) =>
  del<undefined, boolean>(`${getPrefix(knowledgeId, documentId)}/${paragraphId}`)

/** 调整分段顺序，由服务端同步更新受影响的分段位置。 */
const putParagraphPosition = (knowledgeId: string, documentId: string, paragraphId: string, position: number) =>
  put<undefined, void>(`${getPrefix(knowledgeId, documentId)}/adjust_position`, undefined, {
    paragraph_id: paragraphId,
    new_position: position,
  })

export default {
  getParagraphPage,
  postParagraph,
  getParagraphDetail,
  putParagraph,
  postParagraphProblem,
  getParagraphProblems,
  putAssociateParagraphProblem,
  putUnassociateParagraphProblem,
  putMigrateParagraphs,
  putGenerateParagraphQuestions,
  putBatchDeleteParagraphs,
  deleteParagraph,
  putParagraphPosition,
}
