import { del, get, getExportFile, post, put } from '../../core/request'
import type { ParamsPage, ResponsePage } from '../../core/types'
import type {
  Dict,
  KnowledgeTagGroup,
  KnowledgeDetail,
  KnowledgeItem,
  KnowledgeCreatePayload,
  WebKnowledgeCreatePayload,
  LarkKnowledgeCreatePayload,
} from '@/api/types'
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

/** 对知识库中的文档重新向量化。 */
const putReEmbeddingKnowledge = (knowledgeId: string) => {
  return put<undefined, boolean>(`${getPrefix()}/${knowledgeId}/embedding`)
}

/** 批量删除工作空间知识库。 */
const putBatchDeleteKnowledge = (knowledgeIds: string[]) => {
  return put<{ id_list: string[] }, boolean>(`${getPrefix()}/batch_delete`, { id_list: knowledgeIds })
}

/** 批量转移工作空间知识库。 */
const putBatchMoveKnowledge = (knowledgeIds: string[], folderId: string) => {
  return put<{ id_list: string[]; folder_id: string }, boolean>(`${getPrefix()}/batch_move`, { id_list: knowledgeIds, folder_id: folderId })
}

/** 将知识库文档导出为 Excel。 */
const exportKnowledgeExcel = (knowledgeId: string, knowledgeName: string) => {
  return getExportFile(`${knowledgeName}.xlsx`, `${getPrefix()}/${knowledgeId}/export`)
}

/** 将知识库文档及图片导出为 ZIP。 */
const exportKnowledgeZip = (knowledgeId: string, knowledgeName: string) => {
  return getExportFile(`${knowledgeName}.zip`, `${getPrefix()}/${knowledgeId}/export_zip`)
}

/** 导出可用于导入创建的知识库压缩包。 */
const exportKnowledge = (knowledgeId: string, knowledgeName: string) => {
  return getExportFile(`${knowledgeName}.zip`, `${getPrefix()}/${knowledgeId}/export_knowledge`)
}

/** 导入知识库文件并在指定文件夹创建知识库。 */
const postKnowledgeImport = (file: File, folderId: string) => {
  const payload = new FormData()
  payload.append('file', file)
  payload.append('folder_id', folderId)
  return post<FormData, { knowledge_id: string; type: KnowledgeItem['type'] }>(`${getPrefix()}/import_knowledge`, payload)
}

/** 获取知识库外部检索服务生成的 MCP 连接配置。 */
const getKnowledgeMcpConfig = (knowledgeId: string): Promise<string> =>
  get<{ mcp_config: Record<string, unknown> }>(`${getPrefix()}/${knowledgeId}/external_service`).then(({ mcp_config }) =>
    JSON.stringify(mcp_config, null, 2),
  )

/** 提交知识库分词索引任务。 */
const putKnowledgeKeywordIndex = (knowledgeId: string) => put<undefined, void>(`${getPrefix()}/${knowledgeId}/tokenize`)

/** 获取知识库按标签名称分组的标签选项。 */
const getKnowledgeTags = (knowledgeId: string) => get<KnowledgeTagGroup[]>(`${getPrefix()}/${knowledgeId}/tags`)

export default {
  getKnowledgeTags,
  getKnowledgeMcpConfig,
  putKnowledgeKeywordIndex,
  exportKnowledgeExcel,
  exportKnowledgeZip,
  exportKnowledge,
  postKnowledge,
  postWebKnowledge,
  postLarkKnowledge,
  deleteKnowledge,
  getAllKnowledge,
  getKnowledgeDetail,
  getKnowledgePage,
  putKnowledge,
  putLarkKnowledge,
  putReEmbeddingKnowledge,
  putBatchDeleteKnowledge,
  putBatchMoveKnowledge,
  postKnowledgeImport,
}
