import { post, put } from '@/api/admin/core/request'
import type { DocumentItem, DocumentStrategy, ImageDocumentPreview } from '@/api/types'
import { getWorkspaceId } from '@/utils/resource-context'

const getPrefix = (knowledgeId: string) => `/workspace/${getWorkspaceId()}/knowledge/${knowledgeId}/document/image`

/** 按图片处理策略上传图片并生成预览。 */
const postUploadImagePreview = (knowledgeId: string, files: File[], strategy: DocumentStrategy) => {
  const data = new FormData()
  files.forEach((file) => data.append('file', file))
  data.append('doc_strategy', JSON.stringify(strategy))
  return post<FormData, ImageDocumentPreview[]>(`${getPrefix(knowledgeId)}/preview`, data)
}

/** 将已上传的图片预览导入知识库。 */
const putBatchCreateImageDocuments = (knowledgeId: string, previewIds: string[]) =>
  put<{ preview_ids: string[] }, DocumentItem[]>(`${getPrefix(knowledgeId)}/batch_create`, { preview_ids: previewIds })

export default {
  postUploadImagePreview,
  putBatchCreateImageDocuments,
}
