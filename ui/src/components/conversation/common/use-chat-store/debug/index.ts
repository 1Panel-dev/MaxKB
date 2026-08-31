import { ref, computed, watch } from 'vue'
import { useRoute } from 'vue-router'
import { debugApi } from '../../../api'
import { useStreamManager } from '../shared/use-stream-manager'
import { useMessagePagination } from '../shared/use-message-pagination'
import { useConversationCrud } from '../shared/use-conversation-crud'
import { aggregators, Scroll } from '../../../index'
import type { ChatMessage } from '../../types'

// ── 共享状态（单例） ─────────────────────────────────────
const appInfo = ref<{ name: string; icon: string } | null>(null)
const currentChatId = ref('')
let currentApplicationId = ''
const loading = ref<boolean>(false)

// ── 会话 CRUD ─────────────────────────────────────────
const { conversations, loadConversations, loadMore } = useConversationCrud({
  pageConversationAPI: (query: any) =>
    debugApi.history(query.currentPage, query.pageSize, currentApplicationId),
})

// ── 消息分页 ─────────────────────────────────────────
const { messages, hasMore, loadMessages, loadMoreMessages, pushMessage, resetMsgState } =
  useMessagePagination(
    {
      pageConversationMessage: (cid: string, query: any) =>
        debugApi.records(cid, query.currentPage, query.pageSize, currentApplicationId),
    },
    loading,
  )

// ── 流式管理 ─────────────────────────────────────────
const streamManager = useStreamManager()

// ── 计算属性 ─────────────────────────────────────────
const currentConversation = computed(
  () => conversations.value.find((c) => c.id === currentChatId.value) || null,
)

export function useDebugStore() {
  const route = useRoute()
  const applicationId = computed(
    () => (route.params.id as string) || (route.params.applicationId as string) || '',
  )

  // 更新当前 applicationId
  watch(
    applicationId,
    (newId) => {
      currentApplicationId = newId
    },
    { immediate: true },
  )

  const fetchAppInfo = async (appId?: string) => {
    try {
      const { getApi } = await import('../../../api')
      const api = getApi('DEBUG')
    } catch (e) {
      // 静默处理
    }
  }

  // ── 流式聚合（内部） ─────────────────────────────────
  const appendChunk = (message: ChatMessage, chunk: any) => {
    if (!chunk) return
    const contentArray = Array.isArray(chunk.content) ? chunk.content : chunk.type ? [chunk] : null
    if (!contentArray) return

    contentArray.forEach((item: any) => {
      if (!item?.type) return
      const aggregator = aggregators[item.type]
      if (!aggregator) return
      const index = message.content.findIndex((c: any) => c.id === item.id && c.type === item.type)
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
    return await debugApi.open(appId || applicationId.value)
  }

  const deleteChat = async (id: string) => {
    await debugApi.deleteChat(id, applicationId.value)
    const idx = conversations.value.findIndex((c) => c.id === id)
    if (idx >= 0) conversations.value.splice(idx, 1)
  }

  const renameChat = async (id: string, name: string) => {
    await debugApi.modifyChat(id, { abstract: name }, applicationId.value)
    const c = conversations.value.find((x) => x.id === id)
    if (c) c.abstract = name
  }

  const chat = (chatId: string, data: any) => debugApi.chat(chatId, data, currentApplicationId)

  // ── 文件上传 ─────────────────────────────────────────
  const uploadFile = async (file: File, chatId: string): Promise<{ url: string; name: string }> => {
    loading.value = true
    let cid = chatId
    if (!cid) {
      cid = await openChat(applicationId.value)
    }
    const res = await debugApi.uploadFile(file, cid)
    loading.value = false
    return { url: res, name: file.name }
  }

  // ── 切换对话 ─────────────────────────────────────────
  const switchConversation = async (cid: string) => {
    loading.value = true
    await streamManager.switchConversation({
      cid,
      loadMessages,
      resumeStream: (chatRecordId: string) => debugApi.resumeStream(cid, chatRecordId, currentApplicationId),
      getLastMessage: () => messages.value[messages.value.length - 1] ?? null,
      onStream: (chunk) => {
        const lastMsg = messages.value[messages.value.length - 1]
        if (lastMsg) appendChunk(lastMsg, chunk)
      },
      onFinish: () => {
        loading.value = false
      },
      onFailure: () => {
        loading.value = false
      },
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
    startStream: streamManager.startStream,
    switchConversation,
    closeStream: streamManager.closeStream,
    stopWorkflow: (cid: string) => streamManager.stopWorkflow(cid, 'debug', currentApplicationId),
    cancelWorkflow: (cid: string) => streamManager.cancelWorkflow(cid, 'debug', currentApplicationId),
    // 文件
    uploadFile,
  }
}
