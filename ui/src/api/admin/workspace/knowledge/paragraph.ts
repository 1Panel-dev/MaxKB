import { get, post } from '../../core/request'
import type { ParagraphCreatePayload, ParagraphItem, ParagraphQuery } from '@/api/types'
import { getWorkspaceId } from '@/utils/resource-context'

const getPrefix = (knowledgeId: string, documentId: string) =>
  `/workspace/${getWorkspaceId()}/knowledge/${knowledgeId}/document/${documentId}/paragraph`

/** 查询文档的全部分段，按位置排序，支持标题和内容筛选。 */
const getParagraphList = (knowledgeId: string, documentId: string, query?: ParagraphQuery) =>
  get<ParagraphItem[]>(getPrefix(knowledgeId, documentId), { ...query })

/** 在文档首位新增分段，由服务端触发索引。 */
const postParagraph = (knowledgeId: string, documentId: string, payload: ParagraphCreatePayload) =>
  post<ParagraphCreatePayload, ParagraphItem>(getPrefix(knowledgeId, documentId), payload)

export default { getParagraphList, postParagraph }
