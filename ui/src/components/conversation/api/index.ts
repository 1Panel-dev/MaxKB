/**
 * 会话组件的请求封装。
 *
 * 普通请求统一走各自应用的 core 请求客户端（admin：`@/api/admin/core/request`，
 * chat：`@/api/chat/core/request`），返回已解包的业务数据。
 * 唯一的例外是流式对话：core 客户端基于 axios，无法读取 SSE 流，因此这里就地用 fetch
 * 封装 `postStream`，返回原始 `Response` 交给 `ConversationStream` 解析。
 */

import {
  get as adminGet,
  post as adminPost,
  put as adminPut,
  del as adminDel,
} from '@/api/admin/core/request'
import {
  get as chatGet,
  post as chatPost,
  put as chatPut,
  del as chatDel,
} from '@/api/chat/core/request'
import { useStore } from '@/stores'
import { getWorkspaceId } from '@/utils/resource-context'

const trimTrailingSlash = (value: string) => value.replace(/\/+$/, '')
const adminApiBase =
  trimTrailingSlash(window.MaxKB?.prefix || import.meta.env.VITE_BASE_PATH || '/admin/') + '/api'

const chatApiBase =
  trimTrailingSlash(window.MaxKB?.chatPrefix || import.meta.env.VITE_BASE_PATH || '/chat/') + '/api'

/** 发送流式 POST 请求，返回原始 `Response` 供 SSE 读取。 */
function postStream(base: string, path: string, data?: unknown) {
  const { auth, user } = useStore()
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (auth.token) {
    headers['Authorization'] = `Bearer ${auth.token}`
  }
  if (user.language) {
    headers['Accept-Language'] = user.language
  }
  return fetch(`${base}${path.startsWith('/') ? path : `/${path}`}`, {
    method: 'POST',
    headers,
    body: data === undefined ? undefined : JSON.stringify(data),
  })
}

export const debugApi = {
  open: (applicationId: string) =>
    adminGet<any>(`/workspace/${getWorkspaceId()}/application/${applicationId}/open`),

  chat: (chatId: string, data: any, applicationId?: string) =>
    postStream(
      adminApiBase,
      `/workspace/${getWorkspaceId()}/application/${applicationId}/chat/${chatId}/chat_message`,
      data,
    ),

  cancelChat: (chatId: string, applicationId?: string) =>
    adminPost<any, any>(
      `/workspace/${getWorkspaceId()}/application/${applicationId}/chat/${chatId}/cancel_chat_message`,
      {},
    ),

  resumeStream: (chatId: string, chatRecordId: string, applicationId?: string) =>
    postStream(
      adminApiBase,
      `/workspace/${getWorkspaceId()}/application/${applicationId}/chat/${chatId}/chat_record/${chatRecordId}/resume_chat_message`,
    ),

  history: (page: number, size: number, applicationId?: string) => {
    const wsId = getWorkspaceId()
    if (applicationId) {
      return adminGet<any>(
        `/workspace/${wsId}/application/${applicationId}/historical_conversation/${page}/${size}`,
      )
    }
    return adminGet<any>(`/workspace/${wsId}/historical_conversation/${page}/${size}`)
  },

  records: (chatId: string, page: number, size: number, applicationId?: string) => {
    const wsId = getWorkspaceId()
    if (applicationId) {
      return adminGet<any>(
        `/workspace/${wsId}/application/${applicationId}/historical_conversation_record/${chatId}/${page}/${size}`,
      )
    }
    return adminGet<any>(`/workspace/${wsId}/historical_conversation_record/${chatId}/${page}/${size}`)
  },

  deleteChat: (chatId: string, applicationId?: string) => {
    const wsId = getWorkspaceId()
    if (applicationId) {
      return adminDel<any, any>(
        `/workspace/${wsId}/application/${applicationId}/historical_conversation/${chatId}`,
      )
    }
    return adminDel<any, any>(`/workspace/${wsId}/historical_conversation/${chatId}`)
  },

  modifyChat: (chatId: string, data: any, applicationId?: string) => {
    const wsId = getWorkspaceId()
    if (applicationId) {
      return adminPut<any, any>(
        `/workspace/${wsId}/application/${applicationId}/historical_conversation/${chatId}`,
        data,
      )
    }
    return adminPut<any, any>(`/workspace/${wsId}/historical_conversation/${chatId}`, data)
  },

  uploadFile: (file: File, chatId: string) => {
    const fd = new FormData()
    fd.append('file', file)
    fd.append('source_id', chatId)
    fd.append('source_type', 'CHAT')
    return adminPost<FormData, any>('/oss/file', fd)
  },

  speechToText: (data: any) => adminPost<any, any>('/speech_to_text', data),
}

export const chatApi = {
  open: () => chatGet<any>('/open'),

  chat: (chatId: string, data: any) => postStream(chatApiBase, `/chat_message/${chatId}`, data),

  cancelChat: (chatId: string) => chatPost<any, any>(`/chat_message/${chatId}/cancel`, {}),

  resumeStream: (chatId: string, chatRecordId: string) =>
    postStream(chatApiBase, `/chat_message/${chatId}/resume/${chatRecordId}`),

  history: (page: number, size: number) =>
    chatGet<any>(`/historical_conversation/${page}/${size}`),

  records: (chatId: string, page: number, size: number) =>
    chatGet<any>(`/historical_conversation_record/${chatId}/${page}/${size}`),

  deleteChat: (chatId: string) => chatDel<any, any>(`/historical_conversation/${chatId}`),

  modifyChat: (chatId: string, data: any) =>
    chatPut<any, any>(`/historical_conversation/${chatId}`, data),

  uploadFile: (file: File, chatId: string) => {
    const fd = new FormData()
    fd.append('file', file)
    fd.append('source_id', chatId)
    fd.append('source_type', 'CHAT')
    return chatPost<FormData, any>('/oss/file', fd)
  },

  speechToText: (data: any) => chatPost<any, any>('/speech_to_text', data),
}

export type ChatType = 'CHAT' | 'DEBUG'

export function getApi(type: ChatType) {
  return type === 'DEBUG' ? debugApi : chatApi
}
