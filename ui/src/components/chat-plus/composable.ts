import { ref, computed, reactive, type Ref, unref } from 'vue'
import { ConversationStream, aggregators } from './index'
import { useApi, type ChatType } from './api'

export function useChat(type: ChatType | string, applicationId?: string | Ref<string>) {
  const apiType: ChatType = type === 'CHAT' || type === 'ai-chat' ? 'CHAT' : 'DEBUG'
  const api = useApi(apiType)

  const conversations = ref<any[]>([])
  const currentChatId = ref('')
  const messages = ref<any[]>([])
  const msgLoading = ref(false)
  const streamLoading = ref(false)
  let activeStream: any = null

  const currentConversation = computed(() =>
    conversations.value.find((c) => c.id === currentChatId.value),
  )

  const getApplicationId = () => unref(applicationId)

  // ── 会话管理 ─────────────────────────────────────────
  const loadConversations = async (page = 1, size = 50) => {
    const res = await api.history(page, size)
    conversations.value = res.data?.records || []
    return conversations.value
  }

  const openChat = async (appId?: string) => {
    const res = await api.open(appId || getApplicationId())
    currentChatId.value = res.data
    messages.value = []
    return res.data
  }

  const switchChat = async (chatId: string) => {
    currentChatId.value = chatId
    await loadMessages(chatId)
    return chatId
  }

  const deleteChat = async (chatId: string) => {
    await api.deleteChat(chatId)
    conversations.value = conversations.value.filter((c) => c.id !== chatId)
    if (currentChatId.value === chatId) {
      currentChatId.value = conversations.value[0]?.id || ''
    }
  }

  const renameChat = async (chatId: string, name: string) => {
    await api.modifyChat(chatId, { name })
    const chat = conversations.value.find((c) => c.id === chatId)
    if (chat) chat.name = name
  }

  // ── 消息管理 ─────────────────────────────────────────
  const loadMessages = async (chatId?: string, page = 1, size = 20) => {
    const cid = chatId || currentChatId.value
    if (!cid) return []
    msgLoading.value = true
    try {
      const res = await api.records(cid, page, size)
      messages.value = res.data?.records || []
      return messages.value
    } finally {
      msgLoading.value = false
    }
  }

  const pushMessage = (msg: any) => {
    messages.value.push(msg)
  }

  const createAnswerMessage = () => {
    return reactive({
      role: 'ASSISTANT' as const,
      content: [],
      id: '',
      write_ed: false,
    })
  }

  const getOrCreateLastAnswerMessage = () => {
    const last = messages.value[messages.value.length - 1]
    if (last && last.role === 'ASSISTANT') {
      return last
    }
    const msg = createAnswerMessage()
    pushMessage(msg)
    return msg
  }

  // ── 流式聚合 ─────────────────────────────────────────
  const appendChunk = (message: any, chunk: any) => {
    if (!Array.isArray(chunk.content)) return

    const indexList: string[] = message.content.map(
      (c: any) => c.id + '_' + c.type,
    )

    chunk.content.forEach((item: any) => {
      const key = item.id + '_' + item.type
      let i = indexList.indexOf(key)

      if (i < 0) {
        i = indexList.length
        indexList.push(key)
      }

      if (i < message.content.length) {
        const aggregated = aggregators[item.type]?.(message.content[i], item)
        if (aggregated) {
          message.content[i] = aggregated
        }
      } else {
        message.content.push(aggregators[item.type]?.({}, item) || item)
      }
    })
  }

  // ── 发送消息 ─────────────────────────────────────────
  const sendMessage = (
    text: string,
    typeOrOptions?: 'old' | 'new' | { re_chat?: boolean; form_data?: any },
    other_params_data?: any,
  ) => {
    // 兼容旧调用方式: sendMessage(question, type, other_params_data)
    let re_chat = false
    let form_data: any = {}
    if (typeof typeOrOptions === 'string') {
      re_chat = typeOrOptions === 'old'
      form_data = other_params_data || {}
    } else if (typeOrOptions) {
      re_chat = typeOrOptions.re_chat || false
      form_data = typeOrOptions.form_data || {}
    }

    return new Promise<any>((resolve, reject) => {
      if (!currentChatId.value) {
        reject(new Error('No chat open'))
        return
      }

      const aiMsg = createAnswerMessage()
      pushMessage(aiMsg)

      streamLoading.value = true

      const response = api.chat(currentChatId.value, {
        message: text,
        stream: true,
        re_chat,
        form_data,
      })

      activeStream = new ConversationStream(
        response,
        (chunk: any) => appendChunk(aiMsg, chunk),
        () => {
          aiMsg.write_ed = true
          streamLoading.value = false
          activeStream = null
          resolve(aiMsg)
        },
        (e: any) => {
          aiMsg.content.push({ type: 'FAILURE', content: String(e) })
          aiMsg.write_ed = true
          streamLoading.value = false
          activeStream = null
          reject(e)
        },
      )
      activeStream.stream()
    })
  }

  const stopStream = () => {
    activeStream?.cancel()
    streamLoading.value = false
    activeStream = null
  }

  return {
    // 状态
    conversations,
    currentChatId,
    currentConversation,
    messages,
    msgLoading,
    streamLoading,
    // 会话操作
    loadConversations,
    openChat,
    switchChat,
    deleteChat,
    renameChat,
    // 消息操作
    loadMessages,
    pushMessage,
    createAnswerMessage,
    getOrCreateLastAnswerMessage,
    sendMessage,
    stopStream,
  }
}
