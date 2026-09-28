import { get, put } from '../../core/request'
import type { ParamsPage, ResponsePage } from '../../core/types'
import type { Dict, DocumentItem, DocumentQuickCreatePayload } from '@/api/types'
import { getWorkspaceId } from '@/utils/resource-context'

const getPrefix = (knowledgeId: string) => `/workspace/${getWorkspaceId()}/knowledge/${knowledgeId}/document`

/** 获取文档分页列表，支持名称和创建者筛选。 */
const getDocumentPage = (knowledgeId: string, page: ParamsPage, query?: Dict<unknown>) =>
  get<ResponsePage<DocumentItem>>(`${getPrefix(knowledgeId)}/${page.currentPage}/${page.pageSize}`, query)

/** 批量创建仅包含名称的空白文档。 */
const putQuickCreateDocuments = (knowledgeId: string, documents: DocumentQuickCreatePayload[]) =>
  put<DocumentQuickCreatePayload[], DocumentItem[]>(`${getPrefix(knowledgeId)}/batch_create`, documents)

export default { getDocumentPage, putQuickCreateDocuments }
