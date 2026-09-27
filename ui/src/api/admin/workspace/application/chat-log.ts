import { del, get, post, postExportExcel, put } from '../../core/request'
import type { ParamsPage, ResponsePage } from '../../core/types'
import type { ChatLog, Dict } from '@/api/types'
import { getWorkspaceId } from '@/utils/resource-context'

const getPrefix = () => `/workspace/${getWorkspaceId()}/application`

/** 分页获取智能体对话日志。 */
const getChatLog = (applicationId: string, page: ParamsPage, query: Dict<unknown>) =>
  get<ResponsePage<ChatLog>>(`${getPrefix()}/${applicationId}/chat/${page.currentPage}/${page.pageSize}`, query)

/** 导出筛选结果或选中的对话日志。 */
const postExportChatLog = (applicationId: string, applicationName: string, query: Dict<unknown>, data: { select_ids: string[] }) =>
  postExportExcel(`${applicationName}.xlsx`, `${getPrefix()}/${applicationId}/chat/export`, query, data)

/** 保存当前智能体的日志与文件清除策略。 */
const putChatLogCleanTime = (applicationId: string, cleanTime: number, fileCleanTime: number) =>
  put<{ id_list: string[]; clean_time: number; file_clean_time: number }, boolean>(`${getPrefix()}/batch_clean_time`, {
    id_list: [applicationId],
    clean_time: cleanTime,
    file_clean_time: fileCleanTime,
  })

/** 将对话记录添加至知识库。 */
const postChatLogAddKnowledge = (applicationId: string, data: Dict<unknown>) => post(`${getPrefix()}/${applicationId}/add_knowledge`, data)

/** 分页获取对话中的聊天记录。 */
const getChatRecordLog = (applicationId: string, chatId: string, page: ParamsPage, orderAsc = true) =>
  get<ResponsePage<Dict<unknown>>>(`${getPrefix()}/${applicationId}/chat/${chatId}/chat_record/${page.currentPage}/${page.pageSize}`, {
    order_asc: orderAsc,
  })

/** 获取聊天记录详情。 */
const getChatRecordDetails = (applicationId: string, chatId: string, chatRecordId: string) =>
  get<Dict<unknown>>(`${getPrefix()}/${applicationId}/chat/${chatId}/chat_record/${chatRecordId}`)

/** 获取聊天记录的标注段落。 */
const getMarkChatRecord = (applicationId: string, chatId: string, chatRecordId: string) =>
  get<Dict<unknown>[]>(`${getPrefix()}/${applicationId}/chat/${chatId}/chat_record/${chatRecordId}/improve`)

/** 保存聊天记录的知识库标注内容。 */
const putChatRecordLog = (
  applicationId: string,
  chatId: string,
  chatRecordId: string,
  knowledgeId: string,
  documentId: string,
  data: Dict<unknown>,
) => put(`${getPrefix()}/${applicationId}/chat/${chatId}/chat_record/${chatRecordId}/knowledge/${knowledgeId}/document/${documentId}/improve`, data)

/** 删除聊天记录的知识库标注。 */
const deleteMarkChatRecord = (
  applicationId: string,
  chatId: string,
  chatRecordId: string,
  knowledgeId: string,
  documentId: string,
  paragraphId: string,
) =>
  del(
    `${getPrefix()}/${applicationId}/chat/${chatId}/chat_record/${chatRecordId}/knowledge/${knowledgeId}/document/${documentId}/paragraph/${paragraphId}/improve`,
  )

export default {
  getChatLog,
  postExportChatLog,
  putChatLogCleanTime,
  postChatLogAddKnowledge,
  getChatRecordLog,
  getChatRecordDetails,
  getMarkChatRecord,
  putChatRecordLog,
  deleteMarkChatRecord,
}
