import { del, get, getExportFile, post, put } from '@/api/admin/core/request'
import type { Dict, KnowledgeTagGroup, KnowledgeTagPayload, KnowledgeTagUpdatePayload } from '@/api/types'

const getPrefix = (knowledgeId: string) => `/system/resource/knowledge/${knowledgeId}`

/** 获取知识库按标签名称分组的标签选项。 */
const getKnowledgeTags = (knowledgeId: string, query?: Dict<unknown>) => get<KnowledgeTagGroup[]>(`${getPrefix(knowledgeId)}/tags`, query)

/** 创建知识库标签或为已有标签新增值。 */
const postKnowledgeTags = (knowledgeId: string, tags: KnowledgeTagPayload[]) =>
  post<KnowledgeTagPayload[], void>(`${getPrefix(knowledgeId)}/tags`, tags)

/** 重命名知识库标签或编辑单个标签值。 */
const putKnowledgeTag = (knowledgeId: string, tagId: string, tag: KnowledgeTagUpdatePayload) =>
  put<KnowledgeTagUpdatePayload, void>(`${getPrefix(knowledgeId)}/tags/${tagId}`, tag)

/** 删除整个标签分组或单个标签值。 */
const deleteKnowledgeTag = (knowledgeId: string, tagId: string, type: 'key' | 'one') =>
  del<undefined, void>(`${getPrefix(knowledgeId)}/tags/${tagId}/${type}`)

/** 批量删除所选标签，直接提交标签 ID 数组。 */
const putBatchDeleteKnowledgeTags = (knowledgeId: string, tagIds: string[]) =>
  put<string[], void>(`${getPrefix(knowledgeId)}/tags/batch_delete`, tagIds)

/** 导入 Excel 中的知识库标签，重复标签组合由服务端跳过。 */
const postImportKnowledgeTags = (knowledgeId: string, file: File) => {
  const data = new FormData()
  data.append('file', file)
  return post<FormData, void>(`${getPrefix(knowledgeId)}/tags/import`, data)
}

/** 下载知识库标签导入模板。 */
const exportKnowledgeTagTemplate = (knowledgeId: string) => getExportFile('标签模板.xlsx', `${getPrefix(knowledgeId)}/tags/template/export`)

/** 查询文档当前标签。 */
const getDocumentTags = (knowledgeId: string, documentId: string, query?: Dict<unknown>) =>
  get<KnowledgeTagGroup[]>(`${getPrefix(knowledgeId)}/document/${documentId}/tags`, query)

/** 给指定文档批量添加已有标签。 */
const postBatchAddDocumentTags = (knowledgeId: string, documentIds: string[], tagIds: string[]) =>
  post(`${getPrefix(knowledgeId)}/document/batch_add_tag`, { document_ids: documentIds, tag_ids: tagIds })

/** 从单个文档移除指定标签，不删除标签本身。 */
const putDeleteDocumentTags = (knowledgeId: string, documentId: string, tagIds: string[]) =>
  put(`${getPrefix(knowledgeId)}/document/${documentId}/tags/batch_delete`, tagIds)

/** 取消指定标签与单个或多个文档的关联。 */
const putUnlinkTagDocuments = (knowledgeId: string, tagId: string, documentIds: string[]) =>
  put(`${getPrefix(knowledgeId)}/tag/${tagId}/docs_delete`, { id_list: documentIds })

export default {
  getKnowledgeTags,
  postKnowledgeTags,
  putKnowledgeTag,
  deleteKnowledgeTag,
  putBatchDeleteKnowledgeTags,
  postImportKnowledgeTags,
  exportKnowledgeTagTemplate,
  getDocumentTags,
  postBatchAddDocumentTags,
  putDeleteDocumentTags,
  putUnlinkTagDocuments,
}
