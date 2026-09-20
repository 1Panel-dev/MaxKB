import { computed } from 'vue'
import { useRoute } from 'vue-router'
import ConversationApi from '@/api/admin/workspace/conversation'
import FileApi from '@/api/admin/file'
import { FILE_SOURCE_TYPE } from '@/api/enums'
import type { ConversationApiAdapter } from '../../core/types'
import { createConversationListStore } from '../../left-sidebar/conversation-list/index'
import { createMessageListStore } from '../../components/message-list/index'
import { createMessageInputStore } from '../../components/message-input/index'
import { createExecutionDetailStore } from '../../right-sidebar/execution-detail/index'
import type { ConversationBundle } from '../types'

/** debug 模式:装配各组件 store。adapter 走 admin(带 applicationId)。 */
export function createDebugConversation(): ConversationBundle {
  const route = useRoute()
  const appId = computed(
    () => (route.params.id as string) || (route.params.applicationId as string) || '',
  )
  const api: ConversationApiAdapter = {
    pageConversations: (p, s) => ConversationApi.getConversationPage(p, s, appId.value),
    pageRecords: (cid, p, s) => ConversationApi.getConversationRecordPage(cid, p, s, appId.value),
    recordDetail: (cid, rid) => ConversationApi.getConversationRecordDetail(cid, rid, appId.value),
    remove: (id) => ConversationApi.deleteConversation(id, appId.value),
    rename: (id, data) => ConversationApi.putConversation(id, data, appId.value),
    chatMessage: (cid, data) => ConversationApi.postConversationMessage(cid, data, appId.value),
    resumeMessage: (cid, rid) => ConversationApi.postResumeConversationMessage(cid, rid, appId.value),
    uploadFile: (file, cid) => FileApi.postUploadFile(file, cid, FILE_SOURCE_TYPE.CHAT).request,
    cancel: (cid) => ConversationApi.postCancelConversationMessage(cid, appId.value),
  }
  // currentChatId 单一数据源在 list;msgs 只读借用,list 通过 bindLoader 主动驱动加载
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
    getChatId: () => list.currentChatId.value, // 只读 getter,无副作用
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
