import { computed, type Ref } from 'vue'
import { useRoute } from 'vue-router'
import WorkspaceConversationApi from '@/api/admin/workspace/conversation'
import SystemResourceConversationApi from '@/api/admin/system/resource-management/application/conversation'
import { isSystemResource } from '@/utils/resource-context'
import { useStore } from '@/stores'
import FileApi from '@/api/admin/file'
import { FILE_SOURCE_TYPE } from '@/api/enums'
import type { ApplicationDetail } from '@/api/types'
import type { ConversationApiAdapter } from '../../core/types'
import { createConversationListStore } from '../../left-sidebar/conversation-list/index'
import { createMessageListStore } from '../../components/message-list/index'
import { createMessageInputStore } from '../../components/message-input/index'
import { createExecutionDetailStore } from '../../right-sidebar/execution-detail/index'
import type { ConversationBundle } from '../types'
import { useAdminAppInfo } from './app-info'

/**
 * debug 模式:装配各组件 store。adapter 走 admin(带 applicationId)。
 * application 由工作流页提供：每次保存后写回最新详情（当前草稿，含完整工作流），与后端调试执行的工作流一致。
 */
export function createDebugConversation(application: Readonly<Ref<ApplicationDetail | null | undefined>>): ConversationBundle {
  const route = useRoute()
  const ConversationApi = isSystemResource() ? SystemResourceConversationApi : WorkspaceConversationApi
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
    uploadFile: (file, cid, onProgress) => FileApi.postUploadFile(file, cid, FILE_SOURCE_TYPE.CHAT, onProgress).request,
    cancel: (cid) => ConversationApi.postCancelConversationMessage(cid, appId.value),
  }
  const { user } = useStore()
  // 智能体信息随工作流页保存同步，转为 profile 结构后注入各组件 store；知识来源、执行详情在调试中固定显示
  const appInfo = useAdminAppInfo(application, appId)

  // currentChatId 单一数据源在 list;msgs 只读借用,list 通过 bindLoader 主动驱动加载
  const list = createConversationListStore({
    pageConversations: api.pageConversations,
    remove: api.remove,
    rename: api.rename,
    account: computed(() => (user.userInfo ? { nickName: user.userInfo.nick_name, username: user.userInfo.username } : null)),
    appInfo,
  })
  const msgs = createMessageListStore({
    pageRecords: api.pageRecords,
    recordDetail: api.recordDetail,
    chatMessage: api.chatMessage,
    resumeMessage: api.resumeMessage,
    cancel: api.cancel,
    uploadFile: api.uploadFile,
    getChatId: () => list.currentChatId.value, // 只读 getter,无副作用
    appInfo,
  })
  list.bindLoader(msgs.load)
  const input = createMessageInputStore({
    conversations: list.conversations,
    getChatId: list.getChatId,
    renameChat: list.renameChat,
    composerResetSignal: list.composerResetSignal,
    messages: msgs.messages,
    streamLoading: msgs.streamLoading,
    sendMessage: msgs.sendMessage,
    uploadFile: msgs.uploadFile,
    stop: msgs.stop,
    appInfo,
  })
  const detail = createExecutionDetailStore()
  return { appInfo, list, msgs, input, detail }
}
