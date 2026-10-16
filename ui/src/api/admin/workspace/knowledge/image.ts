import { post, put } from '@/api/admin/core/request'
import type { DocumentFileImportPayload, DocumentItem, DocumentStrategy, ImageDocumentPreview } from '@/api/types'
import { getWorkspaceId } from '@/utils/resource-context'

const getPrefix = (knowledgeId: string) => `/workspace/${getWorkspaceId()}/knowledge/${knowledgeId}/document/image`

/** 复用已上传图片，按处理策略生成预览。 */
const postUploadImagePreview = (knowledgeId: string, fileIds: string[], strategy: DocumentStrategy) =>
  post<DocumentFileImportPayload, ImageDocumentPreview[]>(`${getPrefix(knowledgeId)}/preview`, {
    file_id_list: fileIds,
    doc_strategy: strategy,
  })

/** 将已上传的图片预览导入知识库。 */
const putBatchCreateImageDocuments = (knowledgeId: string, previewIds: string[]) =>
  put<{ preview_ids: string[] }, DocumentItem[]>(`${getPrefix(knowledgeId)}/batch_create`, { preview_ids: previewIds })

export default {
  postUploadImagePreview,
  putBatchCreateImageDocuments,
}
