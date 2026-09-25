import { get } from '../../../core/request'
import type { ParamsPage, ResponsePage } from '../../../core/types'
import type { Dict, DocumentItem } from '@/api/types'
import { getWorkspaceId } from '@/utils/resource-context'

const getPrefix = (knowledgeId: string) => `/system/shared/workspace/${getWorkspaceId()}/knowledge/${knowledgeId}/document`

/** 获取工作空间共享知识库的文档分页列表。 */
const getDocumentPage = (knowledgeId: string, page: ParamsPage, query?: Dict<unknown>) =>
  get<ResponsePage<DocumentItem>>(`${getPrefix(knowledgeId)}/${page.currentPage}/${page.pageSize}`, query)

export default { getDocumentPage }
