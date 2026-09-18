import { get, post, put, del, postStream } from './core/request'
import { CHAT_API_BASE_PATH as chatApiBase } from '@/api/constants'

/** 打开对话。 */
const getConversationOpen = () => get('/open')

/** 发送对话消息并返回原始流式响应。 */
const postConversationMessage = (chatId: string, data: unknown) => postStream(chatApiBase, `/chat_message/${chatId}`, data)

/** 取消对话消息生成。 */
const postCancelConversationMessage = (chatId: string) => post(`/chat_message/${chatId}/cancel`, {})

/** 恢复对话消息流。 */
const postResumeConversationMessage = (chatId: string, chatRecordId: string) =>
  postStream(chatApiBase, `/chat_message/${chatId}/resume/${chatRecordId}`)

/** 获取历史会话分页。 */
const getConversationPage = (page: number, size: number) => get(`/historical_conversation/${page}/${size}`)

/** 获取会话记录分页。 */
const getConversationRecordPage = (chatId: string, page: number, size: number) => get(`/historical_conversation_record/${chatId}/${page}/${size}`)

/** 删除会话。 */
const deleteConversation = (chatId: string) => del(`/historical_conversation/${chatId}`)

/** 修改会话信息。 */
const putConversation = (chatId: string, data: unknown) => put(`/historical_conversation/${chatId}`, data)

/** 将语音转换为文字。 */
const postSpeechToText = (data: unknown) => post('/speech_to_text', data)

export default {
  getConversationOpen,
  postConversationMessage,
  postCancelConversationMessage,
  postResumeConversationMessage,
  getConversationPage,
  getConversationRecordPage,
  deleteConversation,
  putConversation,
  postSpeechToText,
}
