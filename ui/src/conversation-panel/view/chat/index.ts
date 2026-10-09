import { computed, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ApplicationApi from '@/api/chat/application'
import ConversationApi from '@/api/chat/conversation'
import { useStore } from '@/stores/chat'
import FileApi from '@/api/chat/file'
import { FILE_SOURCE_TYPE } from '@/api/enums'
import type { ConversationApiAdapter } from '../../core/types'
import { createConversationListStore } from '../../left-sidebar/conversation-list/index'
import { createMessageListStore } from '../../components/message-list/index'
import { createMessageInputStore } from '../../components/message-input/index'
import { createExecutionDetailStore } from '../../right-sidebar/execution-detail/index'
import type { ConversationBundle } from '../types'

/** chat 模式的智能体与会话地址来源；单应用与门户的路由不同，由使用方提供。 */
export interface ChatConversationRouting {
  /** 当前对话的智能体 ID，v3 对话接口按智能体划分路径。 */
  getApplicationId: () => string
  /** 地址中的会话 ID，没有时为空字符串。 */
  getRouteChatId: () => string
  /** 将当前会话写入地址；会话 ID 为空表示新建对话。 */
  replaceChatId: (chatId: string) => void
}

/** 单应用对话：智能体 ID 取自守卫写入的应用认证前置配置，会话地址为 /:accessToken/c/:chatId。 */
function useApplicationChatRouting(): ChatConversationRouting {
  const route = useRoute()
  const router = useRouter()
  const { auth } = useStore()

  return {
    getApplicationId: () => auth.applicationId ?? '',
    getRouteChatId: () => (typeof route.params.chatId === 'string' ? route.params.chatId : ''),
    replaceChatId: (chatId) => {
      const { accessToken } = route.params
      void router.replace(chatId ? { name: 'chat-home-detail', params: { accessToken, chatId } } : { name: 'chat-home', params: { accessToken } })
    },
  }
}

/**
 * chat 模式:装配各组件 store。模式差异只在这里的 adapter。
 * 当前会话与地址双向同步，切换智能体时重新加载智能体信息与会话。
 */
export function createChatConversation(routing: ChatConversationRouting = useApplicationChatRouting()): ConversationBundle {
  const { getApplicationId, getRouteChatId, replaceChatId } = routing
  const { user } = useStore()

  const api: ConversationApiAdapter = {
    // 门户首页尚未确定智能体时没有会话可加载
    pageConversations: (p, s) => (getApplicationId() ? ConversationApi.getConversationPage(getApplicationId(), p, s) : Promise.resolve({ records: [] })),
    pageRecords: (cid, p, s) => ConversationApi.getConversationRecordPage(getApplicationId(), cid, p, s),
    recordDetail: (cid, rid) => ConversationApi.getConversationRecordDetail(getApplicationId(), cid, rid),
    remove: (id) => ConversationApi.deleteConversation(getApplicationId(), id),
    rename: (id, data) => ConversationApi.putConversation(getApplicationId(), id, data),
    chatMessage: (cid, data) => ConversationApi.postConversationMessage(getApplicationId(), cid, data),
    resumeMessage: (cid, rid) => ConversationApi.postResumeConversationMessage(getApplicationId(), cid, rid),
    uploadFile: (file, cid, onProgress) => FileApi.postUploadFile(file, cid, FILE_SOURCE_TYPE.CHAT, onProgress).request,
    cancel: (cid) => ConversationApi.postCancelConversationMessage(cid),
  }
  
  const list = createConversationListStore({
    pageConversations: api.pageConversations,
    remove: api.remove,
    rename: api.rename,
    account: computed(() => {
      const profile = user.chatUserProfile
      return profile?.username ? { nickName: profile.nick_name, username: profile.username } : null
    }),
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
    // 门户首页、全部智能体页尚未确定智能体时禁止发送
    disabled: computed(() => !getApplicationId()),
  })
  const detail = createExecutionDetailStore()

  // 智能体名称与图标展示在侧栏与消息列表
  const loadApplicationProfile = () => {
    if (!getApplicationId()) return
    ApplicationApi.getApplicationProfile(getApplicationId()).then(({ name, icon }) => {
      list.appInfo.value = { name, icon }
    })
  }
  loadApplicationProfile()

  // 切换智能体（门户中打开其他智能体的会话）时停止当前生成，重新加载智能体信息与会话列表。
  // 必须先于会话 ID 监听创建：这里先打开新地址的会话，会话 ID 监听随后比较时即可跳过。
  watch(getApplicationId, () => {
    msgs.cancel()
    list.appInfo.value = null
    loadApplicationProfile()
    list.loadConversations()
    const chatId = getRouteChatId()
    if (chatId) list.selectConversation(chatId)
    else list.newConversation()
  })

  // 会话与地址同步：会话列表 Store 不感知路由，由 chat 模式在此处理；debug 模式的地址不含会话 ID，无需同步。
  // 新建对话时 currentChatId 置空；首条消息生成 ID 或切换会话时写入会话 ID。
  watch(
    () => list.currentChatId.value,
    (chatId) => {
      if (chatId !== getRouteChatId()) replaceChatId(chatId)
    },
  )
  // 浏览器前进、后退等地址变化时切换到对应会话
  watch(getRouteChatId, (chatId) => {
    if (chatId === list.currentChatId.value) return
    if (chatId) list.selectConversation(chatId)
    else list.newConversation()
  })
  // 地址中带会话 ID 时打开该会话
  if (getRouteChatId()) list.selectConversation(getRouteChatId())

  return { list, msgs, input, detail }
}
