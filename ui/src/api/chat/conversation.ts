import { get, post, put, del, postStream } from './core/request'
import type { ResponsePage } from './core/types'
import { CHAT_API_BASE_PATH as chatApiBase } from '@/api/constants'
import type { PortalConversationSummary } from '@/api/types'

/** v3 对话接口均按智能体划分资源路径。 */
const getApplicationPath = (applicationId: string) => `/v3/application/${applicationId}`

/** 打开对话。 */
const getConversationOpen = (applicationId: string) => get(`${getApplicationPath(applicationId)}/open`)

/** 发送对话消息并返回原始流式响应。 */
const postConversationMessage = (applicationId: string, chatId: string, data: unknown) =>
  postStream(chatApiBase, `${getApplicationPath(applicationId)}/chat/${chatId}/chat_message`, data)

/** 取消对话消息生成。 */
const postCancelConversationMessage = (chatId: string) => post(`/v3/chat_message/${chatId}/cancel`, {})

/** 恢复对话消息流。对话端后端尚未提供该接口，路径与 Admin 调试对话保持一致。 */
const postResumeConversationMessage = (applicationId: string, chatId: string, chatRecordId: string) =>
  postStream(chatApiBase, `${getApplicationPath(applicationId)}/chat/${chatId}/chat_record/${chatRecordId}/resume_chat_message`)

/** 获取历史会话分页。 */
const getConversationPage = (applicationId: string, page: number, size: number) =>
  get<ResponsePage<PortalConversationSummary>>(`${getApplicationPath(applicationId)}/chat/${page}/${size}`)

/** 获取单条会话记录详情(含执行详情 execution_details、知识来源、tokens、耗时)。 */
const getConversationRecordDetail = (applicationId: string, chatId: string, chatRecordId: string) =>
  get(`${getApplicationPath(applicationId)}/chat/${chatId}/chat_record/${chatRecordId}`)

/** 获取会话记录分页。 */
const getConversationRecordPage = (applicationId: string, chatId: string, page: number, size: number) =>
  get(`${getApplicationPath(applicationId)}/chat/${chatId}/chat_record/${page}/${size}`)

/** 删除会话。 */
const deleteConversation = (applicationId: string, chatId: string) => del(`${getApplicationPath(applicationId)}/chat/${chatId}`)

/** 修改会话信息。 */
const putConversation = (applicationId: string, chatId: string, data: unknown) =>
  put(`${getApplicationPath(applicationId)}/chat/${chatId}`, data)

/** 将语音转换为文字。 */
const postSpeechToText = (applicationId: string, data: unknown) => post(`${getApplicationPath(applicationId)}/speech_to_text`, data)

export default {
  getConversationOpen,
  postConversationMessage,
  postCancelConversationMessage,
  postResumeConversationMessage,
  getConversationPage,
  getConversationRecordDetail,
  getConversationRecordPage,
  deleteConversation,
  putConversation,
  postSpeechToText,
}
