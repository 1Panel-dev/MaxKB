import { del, post, put } from '../../core/request'
import type { KnowledgeTagPayload, KnowledgeTagUpdatePayload } from '@/api/types'
import { getWorkspaceId } from '@/utils/resource-context'

const getPrefix = (knowledgeId: string) => `/workspace/${getWorkspaceId()}/knowledge/${knowledgeId}/tags`

// TODO：接入标签导入、模板下载、整组／多行编辑接口。
// 请求路径、参数和响应类型以 V3 接口协议为准。

/** 创建知识库标签或为已有标签新增值。 */
const postKnowledgeTags = (knowledgeId: string, tags: KnowledgeTagPayload[]) => post<KnowledgeTagPayload[], void>(getPrefix(knowledgeId), tags)

/** 编辑单个知识库标签，不支持多行编辑。 */
const putKnowledgeTag = (knowledgeId: string, tagId: string, tag: KnowledgeTagUpdatePayload) =>
  put<KnowledgeTagUpdatePayload, void>(`${getPrefix(knowledgeId)}/${tagId}`, tag)

/** 删除整个标签分组或单个标签值。 */
const deleteKnowledgeTag = (knowledgeId: string, tagId: string, type: 'key' | 'one') =>
  del<undefined, void>(`${getPrefix(knowledgeId)}/${tagId}/${type}`)

/** 批量删除所选标签，直接提交标签 ID 数组。 */
const putBatchDeleteKnowledgeTags = (knowledgeId: string, tagIds: string[]) => put<string[], void>(`${getPrefix(knowledgeId)}/batch_delete`, tagIds)

export default {
  postKnowledgeTags,
  putKnowledgeTag,
  deleteKnowledgeTag,
  putBatchDeleteKnowledgeTags,
}
