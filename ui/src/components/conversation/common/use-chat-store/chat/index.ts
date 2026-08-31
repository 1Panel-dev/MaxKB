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
  loading,
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
  })

  // ── 会话操作 ─────────────────────────────────────────
  // 本地新建：前端直接生成 chat_id（草稿），不预先请求后端 open；
  // 首次发消息 / 上传时后端会按该 id 现开会话（open-if-missing）。
  const newChat = (): string => {
    const id = crypto.randomUUID()
    currentChatId.value = id
    resetMsgState()
    if (!conversations.value.some((c) => c.id === id)) {
      conversations.value.unshift({ id, abstract: '新建对话' })
    }
    return id
  }

  const openChat = async (appId?: string) => {
    return await chatApi.open()
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
    return { url: res, name: file.name }
  }

  // ── 发送消息 ─────────────────────────────────────────
  const sendMessage = (cid: string, payload: any, aiMsg: ChatMessage) => {
    loading.value = true
    streamManager.startStream({
      cid,
      request: () => chat(cid, payload),
      onStream: (chunk) => {
        appendChunk(aiMsg, chunk)
      },
      onFinish: () => {
        aiMsg.write_ed = true
        loading.value = false
      },
      onFailure: () => {
        aiMsg.write_ed = true
        loading.value = false
      }
    })
  }

  // ── 切换对话 ─────────────────────────────────────────
  const switchConversation = async (cid: string) => {
    await streamManager.switchConversation({
      cid,
      loadMessages,
      resumeStream: (chatRecordId: string) => chatApi.resumeStream(cid, chatRecordId),
      getLastMessage: () => messages.value[messages.value.length - 1] ?? null,
      onStream: (chunk) => {
        const lastMsg = messages.value[messages.value.length - 1]
        if (lastMsg) appendChunk(lastMsg, chunk)
      },
      onFinish: () => {
        const lastMsg = messages.value[messages.value.length - 1]
        if (lastMsg) lastMsg.write_ed = true
      },
      onFailure: () => {
        const lastMsg = messages.value[messages.value.length - 1]
        if (lastMsg) lastMsg.write_ed = true
      }
    })
  }

  return {
    // 状态
    appInfo,
    currentChatId,
    currentConversation,
    conversations,
    messages,
    loading,
    // 路由
    applicationId,
    // 会话
    loadConversations,
    loadMore,
    newChat,
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
    sendMessage,
    startStream: streamManager.startStream,
    switchConversation,
    closeStream: streamManager.closeStream,
    stopWorkflow: (cid: string) => streamManager.stopWorkflow(cid, 'chat'),
    cancelWorkflow: (cid: string) => streamManager.cancelWorkflow(cid, 'chat'),
    // 文件
    uploadFile,
  }
}
