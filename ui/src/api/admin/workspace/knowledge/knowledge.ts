import { del, get, post, put } from '../../core/request'
import type { ParamsPage, ResponsePage } from '../../core/types'
import type { Dict, KnowledgeItem } from '@/api/types'
import { getWorkspaceId } from '@/utils/resource-context'

const getPrefix = () => {
  const workspaceId = getWorkspaceId()
  return `/workspace/${workspaceId}/knowledge`
}

/** 获取工作空间不分页的知识库列表。 */
const getAllKnowledge = (query?: Dict<unknown>) => {
  return get<KnowledgeItem[]>(getPrefix(), query)
}
/** 获取工作空间知识库分页列表。 */
const getKnowledgePage = (page: ParamsPage, query?: Dict<unknown>) => {
  return get<ResponsePage<KnowledgeItem>>(`${getPrefix()}/${page.currentPage}/${page.pageSize}`, query)
}

/** 删除工作空间知识库。 */
const deleteKnowledge = (knowledgeId: string) => {
  return del<boolean>(`${getPrefix()}/${knowledgeId}`)
}

/** 更新工作空间知识库信息。 */
const putKnowledge = (knowledgeId: string, payload: Partial<KnowledgeItem>) => {
  return put<Partial<KnowledgeItem>, KnowledgeItem>(`${getPrefix()}/${knowledgeId}`, payload)
}

/** 更新飞书知识库信息。 */
const putLarkKnowledge = (knowledgeId: string, payload: Partial<KnowledgeItem>) => {
  return put<Partial<KnowledgeItem>, KnowledgeItem>(`${getPrefix()}/lark/${knowledgeId}`, payload)
}

/** 批量删除工作空间知识库。 */
const putBatchDeleteKnowledge = (knowledgeIds: string[]) => {
  return put<{ id_list: string[] }, boolean>(`${getPrefix()}/batch_delete`, { id_list: knowledgeIds })
}

/** 批量转移工作空间知识库。 */
const putBatchMoveKnowledge = (knowledgeIds: string[], folderId: string) => {
  return put<{ id_list: string[]; folder_id: string }, boolean>(`${getPrefix()}/batch_move`, { id_list: knowledgeIds, folder_id: folderId })
}

/** 导入知识库文件。 */
const importKnowledgeBundle = (payload: FormData) => {
  return post<FormData, unknown>(`${getPrefix()}/import_knowledge`, payload)
}

export default {
  deleteKnowledge,
  getAllKnowledge,
  getKnowledgePage,
  putKnowledge,
  putLarkKnowledge,
  putBatchDeleteKnowledge,
  putBatchMoveKnowledge,
  importKnowledgeBundle,
}
