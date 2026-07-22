import { get as adminGet, postStream as adminPostStream, del as adminDel, put as adminPut, post as adminPost } from '@/request/index'
import { get as chatGet, postStream as chatPostStream, del as chatDel, put as chatPut, post as chatPost } from '@/request/chat/index'
import useStore from '@/stores'

const adminPrefix = (window.MaxKB?.prefix || '/admin') + '/api'
const chatPrefix = (window.MaxKB?.prefix || '/chat') + '/api'

export const debugApi = {
  open: (applicationId: string) => {
    const { user } = useStore()
    return adminGet(`/workspace/${user.getWorkspaceId()}/application/${applicationId}/open`, {})
  },

  chat: (chatId: string, data: any) =>
    adminPostStream(`${adminPrefix}/chat_message/${chatId}`, data),

  history: (page: number, size: number, applicationId?: string) => {
    const { user } = useStore()
    const wsId = user.getWorkspaceId()
    if (applicationId) {
      return adminGet(`/workspace/${wsId}/application/${applicationId}/historical_conversation/${page}/${size}`)
    }
    return adminGet(`/workspace/${wsId}/historical_conversation/${page}/${size}`)
  },

  records: (chatId: string, page: number, size: number, applicationId?: string) => {
    const { user } = useStore()
    const wsId = user.getWorkspaceId()
    if (applicationId) {
      return adminGet(`/workspace/${wsId}/application/${applicationId}/historical_conversation_record/${chatId}/${page}/${size}`)
    }
    return adminGet(`/workspace/${wsId}/historical_conversation_record/${chatId}/${page}/${size}`)
  },

  deleteChat: (chatId: string, applicationId?: string) => {
    const { user } = useStore()
    const wsId = user.getWorkspaceId()
    if (applicationId) {
      return adminDel(`/workspace/${wsId}/application/${applicationId}/historical_conversation/${chatId}`)
    }
    return adminDel(`/workspace/${wsId}/historical_conversation/${chatId}`)
  },

  modifyChat: (chatId: string, data: any, applicationId?: string) => {
    const { user } = useStore()
    const wsId = user.getWorkspaceId()
    if (applicationId) {
      return adminPut(`/workspace/${wsId}/application/${applicationId}/historical_conversation/${chatId}`, data)
    }
    return adminPut(`/workspace/${wsId}/historical_conversation/${chatId}`, data)
  },

  uploadFile: (file: File, chatId: string) => {
    const fd = new FormData()
    fd.append('file', file)
    fd.append('source_id', chatId)
    fd.append('source_type', 'CHAT')
    return adminPost('/oss/file', fd)
  },

  speechToText: (data: any) =>
    adminPost(`/speech_to_text`, data),
}

export const chatApi = {
  open: () =>
    chatGet('/open', {}),

  chat: (chatId: string, data: any) =>
    chatPostStream(`${chatPrefix}/chat_message/${chatId}`, data),

  history: (page: number, size: number) =>
    chatGet(`/historical_conversation/${page}/${size}`),

  records: (chatId: string, page: number, size: number) =>
    chatGet(`/historical_conversation_record/${chatId}/${page}/${size}`),

  deleteChat: (chatId: string) =>
    chatDel(`/historical_conversation/${chatId}`),

  modifyChat: (chatId: string, data: any) =>
    chatPut(`/historical_conversation/${chatId}`, data),

  uploadFile: (file: File, chatId: string) => {
    const fd = new FormData()
    fd.append('file', file)
    fd.append('source_id', chatId)
    fd.append('source_type', 'CHAT')
    return chatPost('/oss/file', fd)
  },

  speechToText: (data: any) =>
    chatPost(`/speech_to_text`, data),
}

export type ChatType = 'CHAT' | 'DEBUG'

export function getApi(type: ChatType) {
  return type === 'DEBUG' ? debugApi : chatApi
}
