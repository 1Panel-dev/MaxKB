import { del, downloadRequest, get, getExportFile, post, put } from '../../core/request'
import type { ParamsPage, ResponsePage } from '../../core/types'
import type {
  Dict,
  DocumentGeneratePayload,
  DocumentItem,
  DocumentQuickCreatePayload,
  DocumentSettingPayload,
  DocumentTaskState,
  DocumentTaskType,
  KnowledgeTagGroup,
} from '@/api/types'
import { getWorkspaceId } from '@/utils/resource-context'

const getPrefix = (knowledgeId: string) => `/workspace/${getWorkspaceId()}/knowledge/${knowledgeId}/document`

/** 获取文档分页列表，支持名称和创建者筛选。 */
const getDocumentPage = (knowledgeId: string, page: ParamsPage, query?: Dict<unknown>) =>
  get<ResponsePage<DocumentItem>>(`${getPrefix(knowledgeId)}/${page.currentPage}/${page.pageSize}`, query)

/** 批量创建仅包含名称的空白文档。 */
const putQuickCreateDocuments = (knowledgeId: string, documents: DocumentQuickCreatePayload[]) =>
  put<DocumentQuickCreatePayload[], DocumentItem[]>(`${getPrefix(knowledgeId)}/batch_create`, documents)

/** 更新文档启用状态。 */
const putDocumentActive = (knowledgeId: string, documentId: string, isActive: boolean) =>
  put(`${getPrefix(knowledgeId)}/${documentId}`, { is_active: isActive })

/** 删除单个文档。 */
const deleteDocument = (knowledgeId: string, documentId: string) => del(`${getPrefix(knowledgeId)}/${documentId}`)

/** 批量删除文档。 */
const putBatchDeleteDocuments = (knowledgeId: string, documentIds: string[]) =>
  put(`${getPrefix(knowledgeId)}/batch_delete`, { id_list: documentIds })

/** 批量提交文档向量化。 */
const putBatchRefreshDocuments = (knowledgeId: string, documentIds: string[], stateList: DocumentTaskState[]) =>
  put(`${getPrefix(knowledgeId)}/batch_refresh`, { id_list: documentIds, state_list: stateList })

/** 批量提交文档分词索引。 */
const putBatchTokenizeDocuments = (knowledgeId: string, documentIds: string[], stateList: DocumentTaskState[]) =>
  put(`${getPrefix(knowledgeId)}/batch_tokenize`, { id_list: documentIds, state_list: stateList })

/** 批量取消指定文档任务。 */
const putBatchCancelDocumentTask = (knowledgeId: string, documentIds: string[], taskType: DocumentTaskType) =>
  put(`${getPrefix(knowledgeId)}/batch_cancel_task`, { id_list: documentIds, type: taskType })

/** 保存单个文档的召回及来源设置。 */
const putDocumentSetting = (knowledgeId: string, documentId: string, data: DocumentSettingPayload) =>
  put(`${getPrefix(knowledgeId)}/${documentId}`, data)

/** 批量保存文档召回设置。 */
const putBatchDocumentSetting = (knowledgeId: string, documentIds: string[], data: DocumentSettingPayload) =>
  put(`${getPrefix(knowledgeId)}/batch_hit_handling`, { ...data, id_list: documentIds })

/** 根据文档内容生成关联问题。 */
const putGenerateDocumentQuestions = (knowledgeId: string, data: DocumentGeneratePayload) =>
  put(`${getPrefix(knowledgeId)}/batch_generate_related`, data)

/** 将选中文档迁移至目标知识库。 */
const putMigrateDocuments = (knowledgeId: string, targetKnowledgeId: string, documentIds: string[]) =>
  put(`${getPrefix(knowledgeId)}/migrate/${targetKnowledgeId}`, documentIds)

/** 同步 Web 文档。 */
const putSyncDocuments = (knowledgeId: string, documentIds: string[]) => put(`${getPrefix(knowledgeId)}/batch_sync`, { id_list: documentIds })

/** 同步飞书文档。 */
const putSyncLarkDocuments = (knowledgeId: string, documentIds: string[]) =>
  put(`/workspace/${getWorkspaceId()}/knowledge/lark/${knowledgeId}/_batch`, { id_list: documentIds })

/** 导出所选文档为 Excel 或 ZIP。 */
const exportDocuments = (knowledgeId: string, documentIds: string[], format: 'excel' | 'zip') =>
  downloadRequest(`${getPrefix(knowledgeId)}/${format === 'excel' ? 'batch_export' : 'batch_export_zip'}`, 'POST', documentIds)

/** 下载文档原文件。 */
const downloadDocumentSource = (knowledgeId: string, document: DocumentItem) =>
  getExportFile(document.name, `${getPrefix(knowledgeId)}/${document.id}/download_source_file`)

/** 替换文档原文件。 */
const postReplaceDocumentSource = (knowledgeId: string, documentId: string, file: File) => {
  const data = new FormData()
  data.append('file', file)
  return post(`${getPrefix(knowledgeId)}/${documentId}/replace_source_file`, data)
}

/** 查询文档当前标签。 */
const getDocumentTags = (knowledgeId: string, documentId: string) => get<KnowledgeTagGroup[]>(`${getPrefix(knowledgeId)}/${documentId}/tags`)

/** 批量添加文档标签。 */
const postAddDocumentTags = (knowledgeId: string, documentIds: string[], tagIds: string[]) =>
  post(`${getPrefix(knowledgeId)}/batch_add_tag`, { document_ids: documentIds, tag_ids: tagIds })

/** 移除文档标签关联。 */
const putDeleteDocumentTags = (knowledgeId: string, documentId: string, tagIds: string[]) =>
  put(`${getPrefix(knowledgeId)}/${documentId}/tags/batch_delete`, tagIds)

export default {
  getDocumentPage,
  putQuickCreateDocuments,
  putDocumentActive,
  deleteDocument,
  putBatchDeleteDocuments,
  putBatchRefreshDocuments,
  putBatchTokenizeDocuments,
  putBatchCancelDocumentTask,
  putDocumentSetting,
  putBatchDocumentSetting,
  putGenerateDocumentQuestions,
  putMigrateDocuments,
  putSyncDocuments,
  putSyncLarkDocuments,
  exportDocuments,
  downloadDocumentSource,
  postReplaceDocumentSource,
  getDocumentTags,
  postAddDocumentTags,
  putDeleteDocumentTags,
}
