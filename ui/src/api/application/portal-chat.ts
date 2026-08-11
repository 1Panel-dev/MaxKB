import { get, post } from '@/request/index'
import type { Result } from '@/request/Result'
import type { Ref } from 'vue'

/**
 * Portal chat API - uses admin TokenAuth
 */

/** Open a chat session */
export const openChatSession = (
  workspaceId: string,
  applicationId: string,
  loading?: Ref<boolean>,
): Promise<Result<any>> => {
  return post(
    `/portal/chat/open/${workspaceId}/${applicationId}`,
    undefined,
    undefined,
    loading,
  )
}

/** Send a chat message (non-streaming) */
export const sendChatMessage = (
  chatId: string,
  content: string,
  loading?: Ref<boolean>,
): Promise<Result<any>> => {
  return post(
    `/chat_message/${chatId}`,
    {
      message: { content },
      stream: false,
      re_chat: false,
    },
    undefined,
    loading,
  )
}

/** Get application detail (for prologue/name) */
export const getApplicationDetail = (
  workspaceId: string,
  applicationId: string,
  loading?: Ref<boolean>,
): Promise<Result<any>> => {
  return get(
    `/workspace/${workspaceId}/application/${applicationId}`,
    undefined,
    loading,
  )
}

/** Get conversation history for an application (admin endpoint) */
export const getConversationHistory = (
  workspaceId: string,
  applicationId: string,
  loading?: Ref<boolean>,
): Promise<Result<any[]>> => {
  return get(
    `/workspace/${workspaceId}/application/${applicationId}/historical_conversation/1/100`,
    undefined,
    loading,
  )
}

/** Get conversation messages (admin endpoint) */
export const getConversationMessages = (
  workspaceId: string,
  applicationId: string,
  chatId: string,
  loading?: Ref<boolean>,
): Promise<Result<any[]>> => {
  return get(
    `/workspace/${workspaceId}/application/${applicationId}/historical_conversation_record/${chatId}/1/100`,
    undefined,
    loading,
  )
}
