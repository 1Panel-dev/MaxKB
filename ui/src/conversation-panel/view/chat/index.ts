import ConversationApi from '@/api/chat/conversation'
import FileApi from '@/api/chat/file'
import { FILE_SOURCE_TYPE } from '@/api/enums'
import type { ConversationApiAdapter } from '../../core/types'
import { createConversationListStore } from '../../left-sidebar/conversation-list/index'
import { createMessageListStore } from '../../components/message-list/index'
import { createMessageInputStore } from '../../components/message-input/index'
import { createExecutionDetailStore } from '../../right-sidebar/execution-detail/index'
import type { ConversationBundle } from '../types'

/** chat 模式:装配各组件 store。模式差异只在这里的 adapter。 */
export function createChatConversation(): ConversationBundle {
  const api: ConversationApiAdapter = {
    pageConversations: (p, s) => ConversationApi.getConversationPage(p, s),
    pageRecords: (cid, p, s) => ConversationApi.getConversationRecordPage(cid, p, s),
    recordDetail: (cid, rid) => ConversationApi.getConversationRecordDetail(cid, rid),
    remove: (id) => ConversationApi.deleteConversation(id),
    rename: (id, data) => ConversationApi.putConversation(id, data),
    chatMessage: (cid, data) => ConversationApi.postConversationMessage(cid, data),
    resumeMessage: (cid, rid) => ConversationApi.postResumeConversationMessage(cid, rid),
    uploadFile: (file) => FileApi.postUploadFile(file, '', FILE_SOURCE_TYPE.CHAT).request,
    cancel: (cid) => ConversationApi.postCancelConversationMessage(cid),
  }
  
  const list = createConversationListStore({
    pageConversations: api.pageConversations,
    remove: api.remove,
    rename: api.rename,
  })
  const msgs = createMessageListStore({
    pageRecords: api.pageRecords,
    recordDetail: api.recordDetail,
    chatMessage: api.chatMessage,
    resumeMessage: api.resumeMessage,
    cancel: api.cancel,
    uploadFile: api.uploadFile,
    getChatId: () => list.currentChatId.value,  
  })
  list.bindLoader(msgs.load)
  const input = createMessageInputStore({
    conversations: list.conversations,
    getChatId: list.getChatId,
    renameChat: list.renameChat,
    composerResetSignal: list.composerResetSignal,
    messages: msgs.messages,
    loading: msgs.loading,
    sendMessage: msgs.sendMessage,
    uploadFile: msgs.uploadFile,
    stop: msgs.stop,
  })
  const detail = createExecutionDetailStore()
  return { list, msgs, input, detail }
}
