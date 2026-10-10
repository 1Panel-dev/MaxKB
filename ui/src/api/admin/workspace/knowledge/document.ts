import { del, downloadRequest, get, getExportFile, post, postExportExcel, put } from '../../core/request'
import type { ParamsPage, ResponsePage } from '../../core/types'
import type {
  Dict,
  DocumentGeneratePayload,
  DocumentFileImportPayload,
  DocumentImportPayload,
  DocumentSplitResult,
  DocumentStrategy,
  DocumentItem,
  DocumentQuickCreatePayload,
  DocumentSettingPayload,
  DocumentTaskState,
  DocumentTaskType,
  DocumentUpdatePayload,
  WebDocumentImportPayload,
  LarkDocumentList,
  LarkDocumentImportPayload,
} from '@/api/types'
import { getWorkspaceId } from '@/utils/resource-context'

const getPrefix = (knowledgeId: string) => `/workspace/${getWorkspaceId()}/knowledge/${knowledgeId}/document`

/** 获取文档分页列表，支持名称和创建者筛选。 */
const getDocumentPage = (knowledgeId: string, page: ParamsPage, query?: Dict<unknown>) =>
  get<ResponsePage<DocumentItem>>(`${getPrefix(knowledgeId)}/${page.currentPage}/${page.pageSize}`, query)

/** 批量创建空白文档或导入text文档。 */
const putBatchCreateDocuments = (knowledgeId: string, documents: DocumentQuickCreatePayload[] | DocumentImportPayload[]) =>
  put<DocumentQuickCreatePayload[] | DocumentImportPayload[], DocumentItem[]>(`${getPrefix(knowledgeId)}/batch_create`, documents)

/** 分段预览 */
const postSplitDocuments = (knowledgeId: string, files: File[], strategy: DocumentStrategy) => {
  const data = new FormData()
  files.forEach((file) => data.append('file', file))
  data.append('doc_strategy', JSON.stringify(strategy))
  return post<FormData, DocumentSplitResult[]>(`${getPrefix(knowledgeId)}/split`, data)
}

/** 从已上传表格创建文档，每个 sheet 由服务端创建独立文档。 */
const postImportTableDocumentsByFileIds = (knowledgeId: string, fileIds: string[]) =>
  post<DocumentFileImportPayload, DocumentItem[]>(`${getPrefix(knowledgeId)}/table_by_file_ids`, { file_id_list: fileIds })

/** 从已上传文件创建 QA 问答对文档。 */
const postImportQADocumentsByFileIds = (knowledgeId: string, fileIds: string[]) =>
  post<DocumentFileImportPayload, DocumentItem[]>(`${getPrefix(knowledgeId)}/qa_by_file_ids`, { file_id_list: fileIds })

/** 按地址导入 Web 文档并应用文档处理策略。 */
const postWebDocument = (knowledgeId: string, payload: WebDocumentImportPayload) =>
  post<WebDocumentImportPayload, boolean>(`${getPrefix(knowledgeId)}/web`, payload)

/** 查询飞书文件夹中的文件，支持分页加载。 */
const getLarkDocumentList = (knowledgeId: string, folderToken: string, query: { page_token?: string } = {}) =>
  post<{ page_token?: string }, LarkDocumentList>(`/workspace/${getWorkspaceId()}/knowledge/lark/${knowledgeId}/${folderToken}/doc_list`, query)

/** 导入所选飞书文档，沿用飞书扩展接口。 */
const postImportLarkDocuments = (knowledgeId: string, documents: LarkDocumentImportPayload[]) =>
  post<LarkDocumentImportPayload[], boolean>(`/workspace/${getWorkspaceId()}/knowledge/lark/${knowledgeId}/import`, documents)

/** 下载表格模板。 */
const exportTableDocumentTemplate = (format: 'excel' | 'csv') =>
  getExportFile(`${format}-template.${format === 'excel' ? 'xlsx' : 'csv'}`, '/workspace/knowledge/document/table_template/export', { type: format })

/** 下载 QA 模板。 */
const exportQADocumentTemplate = (format: 'excel' | 'csv') =>
  getExportFile(`${format}-template.${format === 'excel' ? 'xlsx' : 'csv'}`, '/workspace/knowledge/document/template/export', { type: format })

/** 更新文档名称、启用状态或设置，返回保存后的文档。 */
const putDocument = (knowledgeId: string, documentId: string, data: DocumentUpdatePayload) =>
  put<DocumentUpdatePayload, DocumentItem>(`${getPrefix(knowledgeId)}/${documentId}`, data)

/** 删除单个文档。 */
const deleteDocument = (knowledgeId: string, documentId: string) => del(`${getPrefix(knowledgeId)}/${documentId}`)

/** 批量删除文档。 */
const putBatchDeleteDocuments = (knowledgeId: string, documentIds: string[]) =>
  put(`${getPrefix(knowledgeId)}/batch_delete`, { id_list: documentIds })

/** 单个文档向量化。 */
const putDocumentRefresh = (knowledgeId: string, documentId: string, stateList: DocumentTaskState[]) =>
  put(`${getPrefix(knowledgeId)}/${documentId}/refresh`, { state_list: stateList })

/** 批量文档向量化。 */
const putBatchRefreshDocuments = (knowledgeId: string, documentIds: string[], stateList: DocumentTaskState[]) =>
  put(`${getPrefix(knowledgeId)}/batch_refresh`, { id_list: documentIds, state_list: stateList })

/** 单个文档分词索引。 */
const putDocumentTokenize = (knowledgeId: string, documentId: string, stateList: DocumentTaskState[]) =>
  put(`${getPrefix(knowledgeId)}/${documentId}/tokenize`, { state_list: stateList })

/** 批量文档分词索引。 */
const putBatchTokenizeDocuments = (knowledgeId: string, documentIds: string[], stateList: DocumentTaskState[]) =>
  put(`${getPrefix(knowledgeId)}/batch_tokenize`, { id_list: documentIds, state_list: stateList })

/** 单个/批量生成关联问题。 */
const putGenerateDocumentQuestions = (knowledgeId: string, data: DocumentGeneratePayload) =>
  put(`${getPrefix(knowledgeId)}/batch_generate_related`, data)

/** 单个取消文档任务。 */
const putCancelTask = (knowledgeId: string, documentId: string, taskType: DocumentTaskType) =>
  put(`${getPrefix(knowledgeId)}/${documentId}/cancel_task`, { type: taskType })

/** 批量取消指定文档任务。 */
const putBatchCancelDocumentTask = (knowledgeId: string, documentIds: string[], taskType: DocumentTaskType) =>
  put(`${getPrefix(knowledgeId)}/batch_cancel_task`, { id_list: documentIds, type: taskType })

/** 同步单个 Web 文档。 */
const putDocumentSync = (knowledgeId: string, documentId: string) => put(`${getPrefix(knowledgeId)}/${documentId}/sync`)

/** 批量同步 Web 文档。 */
const putMulSyncDocument = (knowledgeId: string, documentIds: string[]) =>
  put<{ id_list: string[] }, boolean>(`${getPrefix(knowledgeId)}/batch_sync`, { id_list: documentIds })

/** 同步单个飞书文档。 */
const putLarkDocumentSync = (knowledgeId: string, documentId: string) =>
  put(`/workspace/${getWorkspaceId()}/knowledge/lark/${knowledgeId}/document/${documentId}/sync`)

/** 批量同步飞书文档。 */
const putMulLarkSyncDocument = (knowledgeId: string, documentIds: string[]) =>
  put<{ id_list: string[] }, boolean>(`/workspace/${getWorkspaceId()}/knowledge/lark/${knowledgeId}/_batch`, { id_list: documentIds })

/** 批量文档设置。 */
const putBatchDocumentSetting = (knowledgeId: string, documentIds: string[], data: DocumentSettingPayload) =>
  put(`${getPrefix(knowledgeId)}/batch_hit_handling`, { ...data, id_list: documentIds })

/** 批量/单个迁移至目标知识库。 */
const putMigrateDocuments = (knowledgeId: string, targetKnowledgeId: string, documentIds: string[]) =>
  put(`${getPrefix(knowledgeId)}/migrate/${targetKnowledgeId}`, documentIds)

/** 将单个文档导出为 Excel。 */
const exportDocument = (knowledgeId: string, documentId: string, documentName: string) =>
  getExportFile(`${documentName.trim()}.xlsx`, `${getPrefix(knowledgeId)}/${documentId}/export`)

/** 将选中文档批量导出为 Excel。 */
const exportMulDocument = (knowledgeId: string, documentIds: string[], knowledgeName: string) =>
  postExportExcel(`${knowledgeName.trim()}.xlsx`, `${getPrefix(knowledgeId)}/batch_export`, undefined, documentIds)

/** 将单个文档及图片导出为 ZIP。 */
const exportDocumentZip = (knowledgeId: string, documentId: string, documentName: string) =>
  getExportFile(`${documentName.trim()}.zip`, `${getPrefix(knowledgeId)}/${documentId}/export_zip`)

/** 将选中文档及图片批量导出为 ZIP。 */
const exportMulDocumentZip = (knowledgeId: string, documentIds: string[], knowledgeName: string) =>
  downloadRequest(`${getPrefix(knowledgeId)}/batch_export_zip`, 'POST', documentIds, undefined, `${knowledgeName.trim()}.zip`)

/** 下载文档原文件。 */
const downloadDocumentSource = (knowledgeId: string, document: DocumentItem) =>
  getExportFile(document.name, `${getPrefix(knowledgeId)}/${document.id}/download_source_file`)

/** 替换文档原文件。 */
const postReplaceDocumentSource = (knowledgeId: string, documentId: string, file: File) => {
  const data = new FormData()
  data.append('file', file)
  return post(`${getPrefix(knowledgeId)}/${documentId}/replace_source_file`, data)
}

export default {
  getDocumentPage,
  putBatchCreateDocuments,
  postSplitDocuments,
  postImportTableDocumentsByFileIds,
  postImportQADocumentsByFileIds,
  postWebDocument,
  getLarkDocumentList,
  postImportLarkDocuments,
  exportTableDocumentTemplate,
  exportQADocumentTemplate,
  putDocument,
  deleteDocument,
  putBatchDeleteDocuments,
  putDocumentRefresh,
  putBatchRefreshDocuments,
  putDocumentTokenize,
  putBatchTokenizeDocuments,
  putCancelTask,
  putBatchCancelDocumentTask,
  putBatchDocumentSetting,
  putGenerateDocumentQuestions,
  putMigrateDocuments,
  putDocumentSync,
  putMulSyncDocument,
  putLarkDocumentSync,
  putMulLarkSyncDocument,
  exportDocument,
  exportMulDocument,
  exportDocumentZip,
  exportMulDocumentZip,
  downloadDocumentSource,
  postReplaceDocumentSource,
}
