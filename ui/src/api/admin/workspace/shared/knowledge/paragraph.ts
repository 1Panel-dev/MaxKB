import { get } from '../../../core/request'
import type { ParamsPage, ResponsePage } from '../../../core/types'
import type { ParagraphDetail, ParagraphItem, ParagraphQuery } from '@/api/types'
import { getWorkspaceId } from '@/utils/resource-context'

const getPrefix = (knowledgeId: string, documentId: string) =>
  `/system/shared/workspace/${getWorkspaceId()}/knowledge/${knowledgeId}/document/${documentId}/paragraph`

/** 分页查询共享知识库文档分段。 */
const getParagraphPage = (knowledgeId: string, documentId: string, page: ParamsPage, query?: ParagraphQuery) =>
  get<ResponsePage<ParagraphItem>>(`${getPrefix(knowledgeId, documentId)}/${page.currentPage}/${page.pageSize}`, { ...query })

/** 查询共享知识库分段正文、召回统计及关联问题。 */
const getParagraphDetail = (knowledgeId: string, documentId: string, paragraphId: string) =>
  get<ParagraphDetail>(`${getPrefix(knowledgeId, documentId)}/${paragraphId}`)

export default { getParagraphPage, getParagraphDetail }
