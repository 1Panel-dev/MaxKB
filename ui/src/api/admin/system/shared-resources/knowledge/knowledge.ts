import { del, get, getExportFile, post, put } from '@/api/admin/core/request'
import type { ParamsPage, ResponsePage } from '@/api/admin/core/types'
import type {
  Dict,
  KnowledgeCreatePayload,
  KnowledgeDetail,
  KnowledgeGeneratePayload,
  KnowledgeItem,
  KnowledgeSyncType,
  KnowledgeWorkflowCreatePayload,
  LarkKnowledgeCreatePayload,
  WebKnowledgeCreatePayload,
} from '@/api/types'

const prefix = '/system/shared/knowledge'

/** 获取 System 共享知识库分页列表。 */
const getKnowledgePage = (page: ParamsPage, query?: Dict<unknown>) => {
  return get<ResponsePage<KnowledgeItem>>(`${prefix}/${page.currentPage}/${page.pageSize}`, query)
}

/** 获取 System 共享知识库详情。 */
const getKnowledgeDetail = (knowledgeId: string) => get<KnowledgeDetail>(`${prefix}/${knowledgeId}`)

/** 创建 System 共享通用知识库。 */
const postKnowledge = (payload: KnowledgeCreatePayload) => post<KnowledgeCreatePayload, KnowledgeItem>(`${prefix}/base`, payload)

/** 创建 System 共享 Web 知识库。 */
const postWebKnowledge = (payload: WebKnowledgeCreatePayload) => post<WebKnowledgeCreatePayload, KnowledgeItem>(`${prefix}/web`, payload)

/** 创建 System 共享飞书知识库。 */
const postLarkKnowledge = (payload: LarkKnowledgeCreatePayload) => post<LarkKnowledgeCreatePayload, KnowledgeItem>(`${prefix}/lark/save`, payload)

/** 创建 System 共享工作流知识库。 */
const postKnowledgeWorkflow = (payload: KnowledgeWorkflowCreatePayload) =>
  post<KnowledgeWorkflowCreatePayload, KnowledgeItem>(`${prefix}/workflow`, payload)

/** 导入知识库压缩包并创建 System 共享知识库。 */
const postKnowledgeImport = (file: File, folderId: string) => {
  const payload = new FormData()
  payload.append('file', file)
  payload.append('folder_id', folderId)
  return post<FormData, { knowledge_id: string; type: KnowledgeItem['type'] }>(`${prefix}/import_knowledge`, payload)
}

/** 更新 System 共享知识库信息。 */
const putKnowledge = (knowledgeId: string, payload: Partial<KnowledgeItem>) =>
  put<Partial<KnowledgeItem>, KnowledgeItem>(`${prefix}/${knowledgeId}`, payload)

/** 删除 System 共享知识库。 */
const deleteKnowledge = (knowledgeId: string) => del<boolean>(`${prefix}/${knowledgeId}`)

/** 根据知识库中的分段生成关联问题。 */
const putGenerateKnowledgeQuestions = (knowledgeId: string, payload: KnowledgeGeneratePayload) => {
  return put(`${prefix}/${knowledgeId}/generate_related`, payload)
}

/** 对知识库中的文档重新向量化。 */
const putReEmbeddingKnowledge = (knowledgeId: string) => put<undefined, boolean>(`${prefix}/${knowledgeId}/embedding`)

/** 同步 System 共享 Web 知识库。 */
const putSyncWebKnowledge = (knowledgeId: string, syncType: KnowledgeSyncType) => {
  return put<undefined, boolean>(`${prefix}/${knowledgeId}/sync`, undefined, { sync_type: syncType })
}

/** 将知识库文档导出为 Excel。 */
const exportKnowledgeExcel = (knowledgeId: string, knowledgeName: string) => getExportFile(`${knowledgeName}.xlsx`, `${prefix}/${knowledgeId}/export`)

/** 将知识库文档及图片导出为 ZIP。 */
const exportKnowledgeZip = (knowledgeId: string, knowledgeName: string) =>
  getExportFile(`${knowledgeName}.zip`, `${prefix}/${knowledgeId}/export_zip`)

/** 导出可用于导入创建的知识库压缩包。 */
const exportKnowledge = (knowledgeId: string, knowledgeName: string) =>
  getExportFile(`${knowledgeName}.zip`, `${prefix}/${knowledgeId}/export_knowledge`)

/** 获取知识库外部检索服务生成的 MCP 连接配置。 */
const getKnowledgeMcpConfig = (knowledgeId: string): Promise<string> =>
  get<{ mcp_config: Record<string, unknown> }>(`${prefix}/${knowledgeId}/external_service`).then(({ mcp_config }) =>
    JSON.stringify(mcp_config, null, 2),
  )

/** 提交知识库分词索引任务。 */
const putKnowledgeKeywordIndex = (knowledgeId: string) => put<undefined, void>(`${prefix}/${knowledgeId}/tokenize`)

export default {
  deleteKnowledge,
  exportKnowledge,
  exportKnowledgeExcel,
  exportKnowledgeZip,
  getKnowledgeDetail,
  getKnowledgeMcpConfig,
  getKnowledgePage,
  postKnowledge,
  postKnowledgeImport,
  postKnowledgeWorkflow,
  postLarkKnowledge,
  postWebKnowledge,
  putGenerateKnowledgeQuestions,
  putKnowledge,
  putKnowledgeKeywordIndex,
  putReEmbeddingKnowledge,
  putSyncWebKnowledge,
}
