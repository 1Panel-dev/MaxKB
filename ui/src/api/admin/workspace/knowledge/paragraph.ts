import { get, post, put } from '../../core/request'
import type {
  ParagraphCreatePayload,
  ParagraphDetail,
  ParagraphGeneratePayload,
  ParagraphItem,
  ParagraphProblem,
  ParagraphQuery,
  ParagraphUpdatePayload,
} from '@/api/types'
import { getWorkspaceId } from '@/utils/resource-context'

const getPrefix = (knowledgeId: string, documentId: string) =>
  `/workspace/${getWorkspaceId()}/knowledge/${knowledgeId}/document/${documentId}/paragraph`

/** 查询文档的全部分段，按位置排序，支持标题和内容筛选。 */
const getParagraphList = (knowledgeId: string, documentId: string, query?: ParagraphQuery) =>
  get<ParagraphItem[]>(getPrefix(knowledgeId, documentId), { ...query })

/** 在文档首位新增分段，由服务端触发索引。 */
const postParagraph = (knowledgeId: string, documentId: string, payload: ParagraphCreatePayload) =>
  post<ParagraphCreatePayload, ParagraphDetail>(getPrefix(knowledgeId, documentId), payload)

/** 查询分段正文、召回统计及关联问题。 */
const getParagraphDetail = (knowledgeId: string, documentId: string, paragraphId: string) =>
  get<ParagraphDetail>(`${getPrefix(knowledgeId, documentId)}/${paragraphId}`)

/** 保存分段标题和内容，提取后端编辑响应中的最新详情。 */
const putParagraph = (knowledgeId: string, documentId: string, paragraphId: string, payload: ParagraphUpdatePayload) =>
  put<ParagraphUpdatePayload, [ParagraphDetail, ParagraphUpdatePayload, string]>(
    `${getPrefix(knowledgeId, documentId)}/${paragraphId}`,
    payload,
  ).then(([paragraph]) => paragraph)

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

export default {
  getParagraphList,
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
}
