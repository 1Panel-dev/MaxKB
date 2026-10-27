import { del, get, getExportFile, post, put } from '@/api/admin/core/request'
import type LogicFlow from '@logicflow/core'
import type { ParamsPage, ResponsePage } from '@/api/admin/core/types'
import type {
  KnowledgeHitTestPayload,
  KnowledgeHitTestResult,
  Dict,
  KnowledgeDetail,
  KnowledgeItem,
  KnowledgeGeneratePayload,
  KnowledgeSyncType,
} from '@/api/types'

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
const getKnowledgeDetail = (knowledgeId: string, section?: 'setting' | 'document_strategy') => {
  return get<KnowledgeDetail>(`${prefix}/${knowledgeId}`, { section })
}

/** 删除工作空间知识库。 */
const deleteKnowledge = (knowledgeId: string) => {
  return del<boolean>(`${prefix}/${knowledgeId}`)
}

/** 更新工作空间知识库信息。 */
const putKnowledge = (knowledgeId: string, payload: Partial<KnowledgeItem>) => {
  return put<Partial<KnowledgeItem>, KnowledgeItem>(`${prefix}/${knowledgeId}`, payload)
}

/** 更新飞书知识库信息。 */
const putLarkKnowledge = (knowledgeId: string, payload: Partial<KnowledgeItem>) => {
  return put<Partial<KnowledgeItem>, KnowledgeItem>(`${prefix}/lark/${knowledgeId}`, payload)
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
const putSyncWebKnowledge = (knowledgeId: string, syncType: KnowledgeSyncType) => {
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
const exportKnowledge = (knowledgeId: string, knowledgeName: string, withSourceFile: boolean) => {
  return getExportFile(`${knowledgeName}.zip`, `${prefix}/${knowledgeId}/export_knowledge`, { with_source_file: withSourceFile })
}

/** 获取知识库外部检索服务生成的 MCP 连接配置。 */
const getKnowledgeMcpConfig = (knowledgeId: string): Promise<string> =>
  get<{ mcp_config: Record<string, unknown> }>(`${prefix}/${knowledgeId}/mcp_config`).then(({ mcp_config }) =>
    JSON.stringify(mcp_config, null, 2),
  )

/** 提交知识库分词索引任务。 */
const putKnowledgeKeywordIndex = (knowledgeId: string) => put<undefined, void>(`${prefix}/${knowledgeId}/tokenize`)

/** 将系统资源管理知识库转换为工作流知识库，保留已有文档。 */
const postTransformWorkflow = (knowledgeId: string, payload: { work_flow: LogicFlow.GraphConfigData }) =>
  post<{ work_flow: LogicFlow.GraphConfigData }, boolean>(`${prefix}/${knowledgeId}/transform_workflow`, payload)

/** 测试知识库检索并返回命中的分段。 */
const postKnowledgeHitTest = (knowledgeId: string, payload: KnowledgeHitTestPayload) =>
  post<KnowledgeHitTestPayload, KnowledgeHitTestResult[]>(`${prefix}/${knowledgeId}/hit_test`, payload)

export default {
  postKnowledgeHitTest,
  postTransformWorkflow,
  putKnowledgeKeywordIndex,
  exportKnowledgeExcel,
  exportKnowledgeZip,
  exportKnowledge,
  deleteKnowledge,
  getAllKnowledge,
  getKnowledgeDetail,
  getKnowledgePage,
  putKnowledge,
  putLarkKnowledge,
  putReEmbeddingKnowledge,
  putGenerateKnowledgeQuestions,
  getKnowledgeMcpConfig,
  putSyncWebKnowledge,
}
