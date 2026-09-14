import { del, get, post, put } from '../../core/request'
import type { ParamsPage, ResponsePage } from '../../core/types'
import type { Dict, KnowledgeDetail, KnowledgeItem, KnowledgeCreatePayload, WebKnowledgeCreatePayload, LarkKnowledgeCreatePayload } from '@/api/types'
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

/** 获取工作空间知识库详情。 */
const getKnowledgeDetail = (knowledgeId: string) => {
  return get<KnowledgeDetail>(`${getPrefix()}/${knowledgeId}`)
}

/** 创建通用知识库。 */
const postKnowledge = (payload: KnowledgeCreatePayload) => {
  return post<KnowledgeCreatePayload, KnowledgeItem>(`${getPrefix()}/base`, payload)
}

/** 创建 Web 知识库。 */
const postWebKnowledge = (payload: WebKnowledgeCreatePayload) => {
  return post<WebKnowledgeCreatePayload, KnowledgeItem>(`${getPrefix()}/web`, payload)
}

/** 创建飞书知识库，沿用飞书扩展接口。 */
const postLarkKnowledge = (payload: LarkKnowledgeCreatePayload) => {
  return post<LarkKnowledgeCreatePayload, KnowledgeItem>(`${getPrefix()}/lark/save`, payload)
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
  postKnowledge,
  postWebKnowledge,
  postLarkKnowledge,
  deleteKnowledge,
  getAllKnowledge,
  getKnowledgeDetail,
  getKnowledgePage,
  putKnowledge,
  putLarkKnowledge,
  putBatchDeleteKnowledge,
  putBatchMoveKnowledge,
  importKnowledgeBundle,
}
