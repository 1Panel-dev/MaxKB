import { del, get, post, put } from '@/api/admin/core/request'
import type { ParamsPage, ResponsePage } from '@/api/admin/core/types'
import type { TermbaseItem, TermbaseUpdatePayload } from '@/api/types'

const getPrefix = (knowledgeId: string) => `/system/shared/knowledge/${knowledgeId}/termbase`

/** 批量创建知识库自定义分词条目。 */
const postTermbases = (knowledgeId: string, contents: string[]) => post<string[], TermbaseItem[]>(getPrefix(knowledgeId), contents)

/** 分页查询知识库自定义分词条目，支持内容搜索。 */
const getTermbasePage = (knowledgeId: string, page: ParamsPage, query?: { content?: string }) =>
  get<ResponsePage<TermbaseItem>>(`${getPrefix(knowledgeId)}/${page.currentPage}/${page.pageSize}`, query)

/** 编辑单个知识库自定义分词条目。 */
const putTermbase = (knowledgeId: string, termbaseId: string, payload: TermbaseUpdatePayload) =>
  put<TermbaseUpdatePayload, void>(`${getPrefix(knowledgeId)}/${termbaseId}`, payload)

/** 删除单个知识库自定义分词条目。 */
const deleteTermbase = (knowledgeId: string, termbaseId: string) => del<undefined, boolean>(`${getPrefix(knowledgeId)}/${termbaseId}`)

/** 批量删除知识库自定义分词条目。 */
const putBatchDeleteTermbases = (knowledgeId: string, termbaseIds: string[]) =>
  put<string[], boolean>(`${getPrefix(knowledgeId)}/batch_delete`, termbaseIds)

/** 导出所选自定义分词条目的换行文本。 */
const postExportTermbases = (knowledgeId: string, termbaseIds: string[]) =>
  post<string[], string>(`${getPrefix(knowledgeId)}/batch_export`, termbaseIds)

export default {
  postTermbases,
  getTermbasePage,
  putTermbase,
  deleteTermbase,
  putBatchDeleteTermbases,
  postExportTermbases,
}
