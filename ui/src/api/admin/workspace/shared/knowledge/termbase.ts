import { get } from '../../../core/request'
import type { ParamsPage, ResponsePage } from '../../../core/types'
import type { TermbaseItem } from '@/api/types'
import { getWorkspaceId } from '@/utils/resource-context'

const getPrefix = (knowledgeId: string) => `/system/shared/workspace/${getWorkspaceId()}/knowledge/${knowledgeId}/termbase`

/** 分页查询工作空间共享知识库的自定义分词条目，只提供只读访问。 */
// TODO：V3 后端需确认并提供工作空间共享知识库的 termbase 分页查询路由。
const getTermbasePage = (knowledgeId: string, page: ParamsPage, query?: { content?: string }) =>
  get<ResponsePage<TermbaseItem>>(`${getPrefix(knowledgeId)}/${page.currentPage}/${page.pageSize}`, query)

export default { getTermbasePage }
