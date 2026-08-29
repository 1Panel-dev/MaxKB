import { del, get } from '../../core/request'
import type { ParamsPage, ResponsePage } from '../../core/types'
import type { Dict, KnowledgeItem } from '@/api/types'
import { getWorkspaceId } from '@/utils/resource-context'

const getPrefix = () => {
  const workspaceId = getWorkspaceId()
  return `/workspace/${workspaceId}/knowledge`
}

/** 获取工作空间知识库分页列表。 */
const getKnowledgePage = (page: ParamsPage, query?: Dict<unknown>) => {
  return get<ResponsePage<KnowledgeItem>>(
    `${getPrefix()}/${page.currentPage}/${page.pageSize}`,
    query,
  )
}

/** 删除工作空间知识库。 */
const deleteKnowledge = (knowledgeId: string) => {
  return del<boolean>(`${getPrefix()}/${knowledgeId}`)
}

export default {
  deleteKnowledge,
  getKnowledgePage,
}
