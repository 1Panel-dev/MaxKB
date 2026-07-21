import { ref, computed } from 'vue'
import { debugApi } from '../../../api'
import { useStreamManager } from '../shared/use-stream-manager'
import { useMessagePagination } from '../shared/use-message-pagination'
import { useConversationCrud } from '../shared/use-conversation-crud'
import { aggregators } from '../../../index'
import type { ChatMessage } from '../../types'

export function useDebugStore(applicationId?: string) {
  const appInfo = ref<{ name: string; icon: string } | null>(null)

  const fetchAppInfo = async (appId?: string) => {
    try {
      const { getApi } = await import('../../../api')
      const api = getApi('DEBUG')
      // 如果有获取应用详情的接口，在这里调用
      // const res = await api.getApplicationDetail(appId || applicationId)
      // appInfo.value = { name: res.data.name, icon: res.data.icon }
    } catch (e) {
      // 静默处理
    }
  }
  // ── 会话 CRUD ─────────────────────────────────────────
  const { conversations, loadConversations, loadMore } = useConversationCrud({
    pageConversationAPI: (query: any) => debugApi.history(query.currentPage, query.pageSize, applicationId),
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
      debugApi.records(cid, query.currentPage, query.pageSize, applicationId),
  })

  // ── 流式管理 ─────────────────────────────────────────
  const streamManager = useStreamManager()

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
  const openChat = async (applicationId: string) => {
    const res = await debugApi.open(applicationId)
    return res.data
  }

  const deleteChat = async (id: string) => {
    await debugApi.deleteChat(id, applicationId)
    const idx = conversations.value.findIndex((c) => c.id === id)
    if (idx >= 0) conversations.value.splice(idx, 1)
  }

  const renameChat = async (id: string, name: string) => {
    await debugApi.modifyChat(id, { name }, applicationId)
    const c = conversations.value.find((x) => x.id === id)
    if (c) c.name = name
  }

  const chat = (chatId: string, data: any) => debugApi.chat(chatId, data)

  // ── 文件上传 ─────────────────────────────────────────
  const uploadFile = async (file: File, chatId: string): Promise<{ url: string; name: string }> => {
    let cid = chatId
    if (!cid) {
      cid = await openChat(applicationId)
    }
    const res = await debugApi.uploadFile(file, cid)
    return { url: res.data, name: file.name }
  }

  return {
    // 状态
    appInfo,
    conversations,
    messages,
    msgLoading,
    hasMore,
    streamLoading: computed(() => false),
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
