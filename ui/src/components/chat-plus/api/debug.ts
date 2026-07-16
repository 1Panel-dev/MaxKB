import { get, postStream, del, put, post } from '@/request/index'
import useStore from '@/stores'

const prefix = (window.MaxKB?.prefix || '/admin') + '/api'

export const open = (applicationId: string) => {
  const { user } = useStore()
  return get(`/workspace/${user.getWorkspaceId()}/application/${applicationId}/open`, {})
}

export const chat = (chatId: string, data: any) =>
  postStream(`${prefix}/chat_message/${chatId}`, data)

export const history = (page: number, size: number) =>
  get(`/historical_conversation/${page}/${size}`)

export const records = (chatId: string, page: number, size: number) =>
  get(`/historical_conversation_record/${chatId}/${page}/${size}`)

export const recordDetail = (chatId: string, recordId: string) =>
  get(`/historical_conversation/${chatId}/record/${recordId}`)

export const vote = (chatId: string, recordId: string, voteStatus: string, reason?: string) =>
  put(`/vote/chat/${chatId}/chat_record/${recordId}`, {
    vote_status: voteStatus,
    ...(reason !== undefined && { vote_reason: reason }),
  })

export const deleteChat = (chatId: string) =>
  del(`/historical_conversation/${chatId}`)

export const clearChat = () =>
  del('/historical_conversation/clear')

export const modifyChat = (chatId: string, data: any) =>
  put(`/historical_conversation/${chatId}`, data)

export const uploadFile = (file: File, sourceId: string, sourceType: string) => {
  const fd = new FormData()
  fd.append('file', file)
  fd.append('source_id', sourceId)
  fd.append('source_type', sourceType)
  return post('/oss/file', fd)
}
