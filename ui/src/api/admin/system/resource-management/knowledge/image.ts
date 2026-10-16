import { post, put } from '@/api/admin/core/request'
import type { DocumentFileImportPayload, DocumentItem, DocumentStrategy, ImageDocumentImportPayload, ImageDocumentPreview } from '@/api/types'

const getPrefix = (knowledgeId: string) => `/system/resource/knowledge/${knowledgeId}/document/image`

/** 复用已上传图片，按处理策略生成预览。 */
const postUploadImagePreview = (knowledgeId: string, fileIds: string[], strategy: DocumentStrategy) =>
  post<DocumentFileImportPayload, ImageDocumentPreview[]>(`${getPrefix(knowledgeId)}/preview`, {
    file_id_list: fileIds,
    doc_strategy: strategy,
  })

/** 将已上传图片或已有预览导入知识库。 */
const putBatchCreateImageDocuments = (knowledgeId: string, payload: ImageDocumentImportPayload) =>
  put<ImageDocumentImportPayload, DocumentItem[]>(`${getPrefix(knowledgeId)}/batch_create`, payload)

export default {
  postUploadImagePreview,
  putBatchCreateImageDocuments,
}
