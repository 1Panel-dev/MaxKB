import { del, get, getExportFile, put } from '@/api/admin/core/request'
import type { ParamsPage, ResponsePage } from '@/api/admin/core/types'
import type { Dict, KnowledgeDetail, KnowledgeItem, KnowledgeGeneratePayload } from '@/api/types'

const prefix = '/system/resource/knowledge'

/** 获取系统资源管理不分页的知识库列表。 */
const getAllKnowledge = (query?: Dict<unknown>) => {
  return get<KnowledgeItem[]>(prefix, query)
}
/** 获取系统资源管理知识库分页列表。 */
const getKnowledgePage = (page: ParamsPage, query?: Dict<unknown>) => {
  return get<ResponsePage<KnowledgeItem>>(`${prefix}/${page.currentPage}/${page.pageSize}`, query)
}

/** 获取系统资源管理知识库详情。 */
const getKnowledgeDetail = (knowledgeId: string) => {
  return get<KnowledgeDetail>(`${prefix}/${knowledgeId}`)
}

/** 删除工作空间知识库。 */
const deleteKnowledge = (knowledgeId: string) => {
  return del<boolean>(`${prefix}/${knowledgeId}`)
}

/** 更新工作空间知识库信息。 */
const putKnowledge = (knowledgeId: string, payload: Partial<KnowledgeItem>) => {
  return put<Partial<KnowledgeItem>, KnowledgeItem>(`${prefix}/${knowledgeId}`, payload)
}

/** 根据知识库中的分段生成关联问题。 */
const putGenerateKnowledgeQuestions = (knowledgeId: string, payload: KnowledgeGeneratePayload) => {
  return put(`${prefix}/${knowledgeId}/generate_related`, payload)
}

/** 对知识库中的文档重新向量化。 */
const putReEmbeddingKnowledge = (knowledgeId: string) => {
  return put<undefined, boolean>(`${prefix}/${knowledgeId}/embedding`)
}

/** 同步 Web 知识库。 */
const putSyncWebKnowledge = (knowledgeId: string, syncType: 'replace' | 'complete') => {
  return put<undefined, boolean>(`${prefix}/${knowledgeId}/sync`, undefined, { sync_type: syncType })
}

/** 将知识库文档导出为 Excel。 */
const exportKnowledgeExcel = (knowledgeId: string, knowledgeName: string) => {
  return getExportFile(`${knowledgeName}.xlsx`, `${prefix}/${knowledgeId}/export`)
}

/** 将知识库文档及图片导出为 ZIP。 */
const exportKnowledgeZip = (knowledgeId: string, knowledgeName: string) => {
  return getExportFile(`${knowledgeName}.zip`, `${prefix}/${knowledgeId}/export_zip`)
}

/** 导出可用于导入创建的知识库压缩包。 */
const exportKnowledge = (knowledgeId: string, knowledgeName: string) => {
  return getExportFile(`${knowledgeName}.zip`, `${prefix}/${knowledgeId}/export_knowledge`)
}

/** 获取知识库外部检索服务生成的 MCP 连接配置。 */
const getKnowledgeMcpConfig = (knowledgeId: string): Promise<string> =>
  get<{ mcp_config: Record<string, unknown> }>(`${prefix}/${knowledgeId}/external_service`).then(({ mcp_config }) =>
    JSON.stringify(mcp_config, null, 2),
  )

/** 提交知识库分词索引任务。 */
const putKnowledgeKeywordIndex = (knowledgeId: string) => put<undefined, void>(`${prefix}/${knowledgeId}/tokenize`)

export default {
  putKnowledgeKeywordIndex,
  exportKnowledgeExcel,
  exportKnowledgeZip,
  exportKnowledge,
  deleteKnowledge,
  getAllKnowledge,
  getKnowledgeDetail,
  getKnowledgePage,
  putKnowledge,
  putReEmbeddingKnowledge,
  putGenerateKnowledgeQuestions,
  getKnowledgeMcpConfig,
  putSyncWebKnowledge,
}
