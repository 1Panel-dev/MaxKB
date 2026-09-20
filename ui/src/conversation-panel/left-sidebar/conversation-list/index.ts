import { ref, computed, inject, type InjectionKey } from 'vue'
import { v4 as uuidv4 } from 'uuid'
import type { Conversation } from '../../core/types'

// 只声明本组件真正用到的依赖(接口隔离到函数级)
export interface ConversationListDeps {
  pageConversations: (page: number, size: number) => Promise<any>
  remove: (id: string) => Promise<any>
  rename: (id: string, data: { abstract: string }) => Promise<any>
}

/**
 * conversation-list 组件 store:本组件独有——会话列表 + 当前会话 + 应用信息 + 左侧开合。
 */
export function createConversationListStore(deps: ConversationListDeps) {
  const { pageConversations, remove, rename } = deps

  // 切换会话时主动驱动 message-list 加载。延迟绑定(view 里 bindLoader(msgs.load)),
  // 以打破「list 需要 msgs.load、msgs 需要 list 的 currentChatId」的实例化环。
  let loadMessages: () => void = () => {}
  const bindLoader = (fn: () => void) => (loadMessages = fn)

  const conversations = ref<Conversation[]>([])
  const currentChatId = ref('')
  const appInfo = ref<{ name: string; icon: string } | null>(null)
  const leftSideOpen = ref(true)
  // composer 重置信号:新建/切换会话时自增,message-input 监听后清空暂存文件与输入
  const composerResetSignal = ref(0)

  const currentConversation = computed(
    () => conversations.value.find((c) => c.id === currentChatId.value) || null,
  )

  // 列表分页
  const pageSize = 50
  const page = ref(1)
  const hasMore = ref(true)

  const loadConversations = async (p = 1) => {
    try {
      const res = await pageConversations(p, pageSize)
      const records = res?.records || []
      conversations.value = p === 1 ? records : [...conversations.value, ...records]
      page.value = p
      hasMore.value = records.length >= pageSize
    } catch (e) {
      // 历史接口在部分模式下可能不存在,静默处理
    }
  }
  const loadMore = async () => {
    if (!hasMore.value) return
    await loadConversations(page.value + 1)
  }

  const resetComposer = () => {
    composerResetSignal.value++
  }

  // 惰性取 chat_id:已有原样返回,为空才前端生成(幂等,保证上传文件 source_id 与发送一致)
  const getChatId = () => {
    if (currentChatId.value) return currentChatId.value
    currentChatId.value = uuidv4()
    return currentChatId.value
  }

  // 先写入单一数据源 currentChatId,再驱动 message-list 加载(load 内部读 currentChatId)
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

  const deleteChat = async (id: string) => {
    await remove(id)
    const idx = conversations.value.findIndex((c) => c.id === id)
    if (idx >= 0) conversations.value.splice(idx, 1)
    if (currentChatId.value === id) {
      currentChatId.value = conversations.value[0]?.id || ''
      loadMessages()
    }
  }

  const renameChat = async (id: string, name: string) => {
    await rename(id, { abstract: name })
    const c = conversations.value.find((x) => x.id === id)
    if (c) c.abstract = name
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
    toggleLeftSide: () => (leftSideOpen.value = !leftSideOpen.value),
  }
}

export type ConversationListStore = ReturnType<typeof createConversationListStore>

export const CONVERSATION_LIST_KEY: InjectionKey<ConversationListStore> = Symbol('conversation-list')

export function useConversationListStore(): ConversationListStore {
  const store = inject(CONVERSATION_LIST_KEY)
  if (!store) throw new Error('useConversationListStore 必须在 ConversationView 内使用')
  return store
}
