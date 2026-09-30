/** 查询文档当前标签。 */
const getDocumentTags = (knowledgeId: string, documentId: string) => get<KnowledgeTagGroup[]>(`${getPrefix(knowledgeId)}/${documentId}/tags`)

/** 批量添加文档标签。 */
const postAddDocumentTags = (knowledgeId: string, documentIds: string[], tagIds: string[]) =>
  post(`${getPrefix(knowledgeId)}/batch_add_tag`, { document_ids: documentIds, tag_ids: tagIds })

/** 移除文档标签关联。 */
const putDeleteDocumentTags = (knowledgeId: string, documentId: string, tagIds: string[]) =>
  put(`${getPrefix(knowledgeId)}/${documentId}/tags/batch_delete`, tagIds)
