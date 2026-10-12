import { del, get, getExportFile, post, put } from '../../core/request'
import type { KnowledgeTagGroup, KnowledgeTagPayload, KnowledgeTagUpdatePayload } from '@/api/types'
import { getWorkspaceId } from '@/utils/resource-context'

const getPrefix = (knowledgeId: string) => `/workspace/${getWorkspaceId()}/knowledge/${knowledgeId}/tags`

/** 获取知识库按标签名称分组的标签选项。 */
const getKnowledgeTags = (knowledgeId: string) => get<KnowledgeTagGroup[]>(getPrefix(knowledgeId))

/** 创建知识库标签或为已有标签新增值。 */
const postKnowledgeTags = (knowledgeId: string, tags: KnowledgeTagPayload[]) => post<KnowledgeTagPayload[], void>(getPrefix(knowledgeId), tags)

/** 重命名知识库标签或编辑单个标签值。 */
const putKnowledgeTag = (knowledgeId: string, tagId: string, tag: KnowledgeTagUpdatePayload) =>
  put<KnowledgeTagUpdatePayload, void>(`${getPrefix(knowledgeId)}/${tagId}`, tag)

/** 删除整个标签分组或单个标签值。 */
const deleteKnowledgeTag = (knowledgeId: string, tagId: string, type: 'key' | 'one') =>
  del<undefined, void>(`${getPrefix(knowledgeId)}/${tagId}/${type}`)

/** 批量删除所选标签，直接提交标签 ID 数组。 */
const putBatchDeleteKnowledgeTags = (knowledgeId: string, tagIds: string[]) => put<string[], void>(`${getPrefix(knowledgeId)}/batch_delete`, tagIds)

/** 导入 Excel 中的知识库标签，重复标签组合由服务端跳过。 */
const postImportKnowledgeTags = (knowledgeId: string, file: File) => {
  const data = new FormData()
  data.append('file', file)
  return post<FormData, void>(`${getPrefix(knowledgeId)}/import`, data)
}

/** 下载知识库标签导入模板。 */
const exportKnowledgeTagTemplate = (knowledgeId: string) => getExportFile('标签模板.xlsx', `${getPrefix(knowledgeId)}/template/export`)

export default {
  getKnowledgeTags,
  postKnowledgeTags,
  putKnowledgeTag,
  deleteKnowledgeTag,
  putBatchDeleteKnowledgeTags,
  postImportKnowledgeTags,
  exportKnowledgeTagTemplate,
}
