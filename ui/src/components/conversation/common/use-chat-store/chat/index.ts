import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { chatApi } from '../../../api'
import { useStreamManager } from '../shared/use-stream-manager'
import { useMessagePagination } from '../shared/use-message-pagination'
import { useConversationCrud } from '../shared/use-conversation-crud'
import { aggregators } from '../../../index'
import type { ChatMessage } from '../../types'

// ── 共享状态（单例） ─────────────────────────────────────
const appInfo = ref<{ name: string; icon: string } | null>(null)
const currentChatId = ref('')

// ── 会话 CRUD ─────────────────────────────────────────
const { conversations, loadConversations, loadMore } = useConversationCrud({
  pageConversationAPI: (query: any) => chatApi.history(query.currentPage, query.pageSize),
})

// ── 消息分页 ─────────────────────────────────────────
const {
  messages,
  msgLoading,
  hasMore,
  loadMessages,
  loadMoreMessages,
  pushMessage,
  resetMsgState,
} = useMessagePagination({
  pageConversationMessage: (cid: string, query: any) =>
    chatApi.records(cid, query.currentPage, query.pageSize),
})

// ── 流式管理 ─────────────────────────────────────────
const streamManager = useStreamManager()

// ── 计算属性 ─────────────────────────────────────────
const currentConversation = computed(() => conversations.value.find(c => c.id === currentChatId.value) || null)

export function useChatStore() {
  const route = useRoute()
  const applicationId = computed(() => route.params.id as string || route.params.applicationId as string || '')

  const fetchAppInfo = async (applicationId?: string) => {
    try {
      // 对话模式下，应用信息通常由外部传入或从路由获取
      // 如果有获取应用详情的接口，在这里调用
    } catch (e) {
      // 静默处理
    }
  }

  // ── 流式聚合（内部） ─────────────────────────────────
  const appendChunk = (message: ChatMessage, chunk: any) => {
    if (!chunk) return
    const contentArray = Array.isArray(chunk.content)
      ? chunk.content
      : chunk.type ? [chunk] : null
    if (!contentArray) return

    contentArray.forEach((item: any) => {
      if (!item?.type) return
      const aggregator = aggregators[item.type]
      if (!aggregator) return
      const index = message.content.findIndex(
        (c: any) => c.id === item.id && c.type === item.type,
      )
      if (index >= 0) {
        message.content[index] = aggregator(message.content[index], item)
      } else {
        message.content.push(aggregator({}, item))
      }
    })
  }

  const createAnswerMessage = (): ChatMessage => ({
    role: 'ASSISTANT',
    content: [],
    id: '',
    write_ed: false,
  })

  // ── 会话操作 ─────────────────────────────────────────
  const openChat = async (appId?: string) => {
    const res = await chatApi.open()
    return res.data
  }

  const deleteChat = async (id: string) => {
    await chatApi.deleteChat(id)
    const idx = conversations.value.findIndex((c) => c.id === id)
    if (idx >= 0) conversations.value.splice(idx, 1)
  }

  const renameChat = async (id: string, name: string) => {
    await chatApi.modifyChat(id, { abstract: name })
    const c = conversations.value.find((x) => x.id === id)
    if (c) c.abstract = name
  }

  const chat = (chatId: string, data: any) => chatApi.chat(chatId, data)

  // ── 文件上传 ─────────────────────────────────────────
  const uploadFile = async (file: File): Promise<{ url: string; name: string }> => {
    const res = await chatApi.uploadFile(file, '')
    return { url: res.data, name: file.name }
  }

  return {
    // 状态
    appInfo,
    currentChatId,
    currentConversation,
    conversations,
    messages,
    msgLoading,
    hasMore,
    streamLoading: computed(() => streamManager.getStreamLoading(currentChatId.value)),
    // 路由
    applicationId,
    // 会话
    loadConversations,
    loadMore,
    openChat,
    deleteChat,
    renameChat,
    fetchAppInfo,
    // 消息
    loadMessages,
    loadMoreMessages,
    pushMessage,
    resetMsgState,
    createAnswerMessage,
    appendChunk,
    // 流式
    chat,
    startStream: streamManager.startStream,
    cancelStream: streamManager.cancelStream,
    getStreamLoading: streamManager.getStreamLoading,
    // 文件
    uploadFile,
  }
}
