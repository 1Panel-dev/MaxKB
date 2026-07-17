import { get as adminGet, postStream as adminPostStream, del as adminDel, put as adminPut } from '@/request/index'
import { get as chatGet, postStream as chatPostStream, del as chatDel, put as chatPut } from '@/request/chat/index'
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

  history: (page: number, size: number) =>
    adminGet(`/historical_conversation/${page}/${size}`),

  records: (chatId: string, page: number, size: number) =>
    adminGet(`/historical_conversation_record/${chatId}/${page}/${size}`),

  deleteChat: (chatId: string) =>
    adminDel(`/historical_conversation/${chatId}`),

  modifyChat: (chatId: string, data: any) =>
    adminPut(`/historical_conversation/${chatId}`, data)
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
    chatPut(`/historical_conversation/${chatId}`, data)
}

export type ChatType = 'CHAT' | 'DEBUG'

export function getApi(type: ChatType) {
  return type === 'DEBUG' ? debugApi : chatApi
}
