import { computed, inject, ref, type InjectionKey } from 'vue'
import { v4 as uuidv4 } from 'uuid'
import type { Conversation } from '../../core/types'

// 由 Chat / Debug 入口注入本组件需要的会话接口。
export interface ConversationListDeps {
  pageConversations: (page: number, size: number) => Promise<{ records?: Conversation[] } | null | undefined>
  remove: (id: string) => Promise<unknown>
  rename: (id: string, data: { abstract: string }) => Promise<unknown>
}

/** 管理左侧会话列表、当前会话和侧栏展示状态。 */
export function createConversationListStore(deps: ConversationListDeps) {
  const { pageConversations, remove, rename } = deps

  // 应用信息与侧栏开合
  const appInfo = ref<{ name: string; icon: string } | null>(null)
  const leftSideOpen = ref(true)

  const toggleLeftSide = () => (leftSideOpen.value = !leftSideOpen.value)

  // 历史会话分页
  const conversations = ref<Conversation[]>([])
  const pageSize = 50
  const currentPage = ref(1)
  const hasMore = ref(true)

  const loadConversations = async (page = 1) => {
    try {
      const response = await pageConversations(page, pageSize)
      const records = response?.records || []
      conversations.value = page === 1 ? records : [...conversations.value, ...records]
      currentPage.value = page
      hasMore.value = records.length >= pageSize
    } catch {
      // 部分模式可能不提供历史接口，加载失败时保留现有列表和分页状态。
    }
  }

  const loadMore = async () => {
    if (!hasMore.value) return
    await loadConversations(currentPage.value + 1)
  }

  // 当前会话与输入区重置
  const currentChatId = ref('')
  const currentConversation = computed(() => conversations.value.find((conversation) => conversation.id === currentChatId.value) || null)
  // 新建或切换会话时递增，由 message-input 监听并清空暂存文件与输入。
  const composerResetSignal = ref(0)

  // View 在两个 Store 创建后绑定加载方法，避免与 message-list 循环初始化。
  let loadMessages: () => void = () => {}
  const bindLoader = (loader: () => void) => (loadMessages = loader)

  const resetComposer = () => {
    composerResetSignal.value++
  }

  // 仅在需要时生成会话 ID，保证上传文件的 source_id 与发送消息使用同一 ID。
  const getChatId = () => {
    if (currentChatId.value) return currentChatId.value
    currentChatId.value = uuidv4()
    return currentChatId.value
  }

  // 消息加载会读取 currentChatId，必须先更新 ID 再触发加载。
  const selectConversation = (id: string) => {
    resetComposer()
    currentChatId.value = id
    loadMessages()
  }

  const newConversation = () => {
    resetComposer()
    currentChatId.value = ''
    loadMessages()
  }

  // 会话维护：请求成功后更新本地列表。
  const deleteChat = async (id: string) => {
    await remove(id)
    const conversationIndex = conversations.value.findIndex((conversation) => conversation.id === id)
    if (conversationIndex >= 0) conversations.value.splice(conversationIndex, 1)

    if (currentChatId.value === id) {
      currentChatId.value = conversations.value[0]?.id || ''
      loadMessages()
    }
  }

  const renameChat = async (id: string, name: string) => {
    await rename(id, { abstract: name })
    const conversation = conversations.value.find((conversation) => conversation.id === id)
    if (conversation) conversation.abstract = name
  }

  return {
    conversations,
    currentChatId,
    currentConversation,
    appInfo,
    leftSideOpen,
    hasMore,
    composerResetSignal,
    loadConversations,
    loadMore,
    resetComposer,
    getChatId,
    bindLoader,
    selectConversation,
    newConversation,
    deleteChat,
    renameChat,
    toggleLeftSide,
  }
}

export type ConversationListStore = ReturnType<typeof createConversationListStore>

// 会话视图内共享 Store
export const CONVERSATION_LIST_KEY: InjectionKey<ConversationListStore> = Symbol('conversation-list')

export function useConversationListStore(): ConversationListStore {
  const store = inject(CONVERSATION_LIST_KEY)
  if (!store) throw new Error('useConversationListStore 必须在 ConversationView 内使用')
  return store
}
