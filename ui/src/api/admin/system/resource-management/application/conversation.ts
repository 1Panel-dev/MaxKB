import { get, post, put, del, postStream } from '@/api/admin/core/request'
import { ADMIN_API_BASE_PATH as adminApiBase } from '@/api/constants'

const getPrefix = (applicationId: string) => `/system/resource/application/${applicationId}`

/** 打开对话。 */
const getConversationOpen = (applicationId: string) => get(`${getPrefix(applicationId)}/open`)

/** 发送对话消息并返回原始流式响应。 */
const postConversationMessage = (chatId: string, data: unknown, applicationId: string) =>
  postStream(adminApiBase, `${getPrefix(applicationId)}/chat/${chatId}/chat_message`, data)

/** 取消对话消息生成。 */
const postCancelConversationMessage = (chatId: string, applicationId: string) =>
  post(`${getPrefix(applicationId)}/chat/${chatId}/cancel_chat_message`, {})

/** 恢复对话消息流。 */
const postResumeConversationMessage = (chatId: string, chatRecordId: string, applicationId: string) =>
  postStream(
    adminApiBase,
    `${getPrefix(applicationId)}/chat/${chatId}/chat_record/${chatRecordId}/resume_chat_message`,
  )

/** 获取历史会话分页。 */
const getConversationPage = (page: number, size: number, applicationId: string) =>
  get(`${getPrefix(applicationId)}/historical_conversation/${page}/${size}`)

/** 获取会话记录详情。 */
const getConversationRecordDetail = (chatId: string, chatRecordId: string, applicationId: string) =>
  get(`${getPrefix(applicationId)}/chat/${chatId}/chat_record/${chatRecordId}`)

/** 获取会话记录分页。 */
const getConversationRecordPage = (chatId: string, page: number, size: number, applicationId: string) =>
  get(`${getPrefix(applicationId)}/historical_conversation_record/${chatId}/${page}/${size}`)

/** 删除会话。 */
const deleteConversation = (chatId: string, applicationId: string) =>
  del(`${getPrefix(applicationId)}/historical_conversation/${chatId}`)

/** 修改会话信息。 */
const putConversation = (chatId: string, data: unknown, applicationId: string) =>
  put(`${getPrefix(applicationId)}/historical_conversation/${chatId}`, data)

/** 使用指定智能体将语音转换为文字。 */
const postSpeechToText = (applicationId: string, data: unknown) =>
  post(`${getPrefix(applicationId)}/speech_to_text`, data)

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
