import { ref, computed, type Ref, unref } from 'vue'
import { aggregators } from './index'
import { getApi, type ChatType } from './api'
import { ConversationStream } from './stream'

interface ChatMessage {
  role: 'USER' | 'ASSISTANT'
  content: any[]
  id: string
}

interface ChatConversation {
  id: string
  name: string
}

export function useChat(type: ChatType, applicationId?: string | Ref<string>) {
  const api = getApi(type)
  const conversations = ref<ChatConversation[]>([])
  const currentChatId = ref('')
  const messages = ref<ChatMessage[]>([])
  const msgLoading = ref(false)
  const streamLoading = ref(false)
  let activeStream: ConversationStream | null = null

  const getApplicationId = () => unref(applicationId)

  const currentConversation = computed(() =>
    conversations.value.find((c) => c.id === currentChatId.value)
  )

  const appInfo = computed(() => ({
    name: 'AI Chat',
    icon: ''
  }))

  const loadConversations = async (page = 1, size = 50) => {
    try {
      const res = await api.history(page, size)
      conversations.value = res.data?.records || []
    } catch (e) {
      console.error('Failed to load conversations:', e)
    }
    return conversations.value
  }

  const openChat = async (appId?: string) => {
    try {
      const id = appId || getApplicationId()
      if (!id) throw new Error('No application ID')
      const res = await api.open(id)
      currentChatId.value = res.data
      messages.value = []
      return res.data
    } catch (e) {
      console.error('Failed to open chat:', e)
      throw e
    }
  }

  const switchChat = async (chatId: string) => {
    currentChatId.value = chatId
    await loadMessages(chatId)
    return chatId
  }

  const deleteChat = async (id: string) => {
    try {
      await api.deleteChat(id)
      conversations.value = conversations.value.filter((c) => c.id !== id)
      if (currentChatId.value === id) {
        currentChatId.value = conversations.value[0]?.id || ''
      }
    } catch (e) {
      console.error('Failed to delete chat:', e)
    }
  }

  const renameChat = async (id: string, name: string) => {
    try {
      await api.modifyChat(id, { name })
      const conv = conversations.value.find((c) => c.id === id)
      if (conv) conv.name = name
    } catch (e) {
      console.error('Failed to rename chat:', e)
    }
  }

  const loadMessages = async (chatId: string) => {
    msgLoading.value = true
    try {
      const res = await api.records(chatId, 1, 100)
      const records = res.data?.records || []
      messages.value = records.map((record: any) => ({
        id: record.id,
        role: 'USER',
        content: [{ type: 'TEXT', content: record.problem_text }]
      }))
      // Add assistant messages
      records.forEach((record: any, index: number) => {
        if (record.answer_text_list) {
          messages.value.splice(index * 2 + 1, 0, {
            id: record.id + '-answer',
            role: 'ASSISTANT',
            content: record.answer_text_list.flat()
          })
        }
      })
    } catch (e) {
      console.error('Failed to load messages:', e)
    } finally {
      msgLoading.value = false
    }
  }

  const createAnswerMessage = (): ChatMessage => {
    return {
      role: 'ASSISTANT',
      content: [],
      id: ''
    }
  }

  const pushMessage = (msg: ChatMessage) => {
    messages.value.push(msg)
  }

  const getOrCreateLastAnswerMessage = (): ChatMessage => {
    const last = messages.value[messages.value.length - 1]
    if (last && last.role === 'ASSISTANT') {
      return last
    }
    const answerMessage = createAnswerMessage()
    pushMessage(answerMessage)
    return answerMessage
  }

  const appendChunk = (message: ChatMessage, chunk: any) => {
    console.log('appendChunk received:', chunk)
    
    if (!chunk) return
    
    // 处理直接包含 content 数组的情况
    let contentArray = chunk.content
    if (!Array.isArray(contentArray)) {
      // 如果 chunk 本身就是一个内容项（如 FORM），包装成数组
      if (chunk.type) {
        contentArray = [chunk]
      } else {
        return
      }
    }

    contentArray.forEach((item: any) => {
      if (!item || !item.type) return
      
      const aggregator = aggregators[item.type]
      if (!aggregator) {
        console.warn('No aggregator for type:', item.type)
        return
      }

      const index = message.content.findIndex(
        (c) => c.id === item.id && c.type === item.type
      )

      if (index >= 0) {
        message.content[index] = aggregator(message.content[index], item)
      } else {
        message.content.push(aggregator({}, item))
      }
    })
    
    console.log('Updated message content:', message.content)
  }

  const sendMessage = async (
    text: string,
    options?: { re_chat?: boolean; form_data?: any; position?: any; chat_record_id?: string; chunk_id?: string; onScroll?: () => void }
  ) => {
    const re_chat = options?.re_chat || false
    const form_data = options?.form_data || {}
    const position = options?.position || null
    const chat_record_id = options?.chat_record_id || null
    const chunk_id = options?.chunk_id || null
    const onScroll = options?.onScroll || (() => {})

    console.log('sendMessage called:', {
      text,
      options,
      re_chat,
      form_data,
      position,
      chat_record_id,
      currentChatId: currentChatId.value
    })

    return new Promise<any>((resolve, reject) => {
      if (!currentChatId.value) {
        console.error('No chat open, currentChatId is empty')
        reject(new Error('No chat open'))
        return
      }

      // 表单提交时，找到包含相同 chunk_id 的消息，否则新建
      let aiMsg: ChatMessage
      if (chunk_id) {
        const existing = messages.value.find(m => 
          m.role === 'ASSISTANT' && 
          m.content.some((c: any) => c.id === chunk_id)
        )
        if (existing) {
          aiMsg = existing
        } else {
          aiMsg = createAnswerMessage()
          pushMessage(aiMsg)
        }
      } else {
        aiMsg = createAnswerMessage()
        pushMessage(aiMsg)
      }

      streamLoading.value = true

      const requestData: any = {
        message: text,
        stream: true,
        re_chat,
        form_data
      }
      
      // position、chat_record_id、chunk_id 与 re_chat 同级别
      if (position) {
        requestData.position = position
      }
      if (chat_record_id) {
        requestData.chat_record_id = chat_record_id
      }
      if (chunk_id) {
        requestData.chunk_id = chunk_id
      }

      console.log('Sending request to API:', {
        chatId: currentChatId.value,
        data: requestData
      })

      const responsePromise = api.chat(currentChatId.value, requestData)

      // postStream 返回 Promise，需要 await
      responsePromise.then((response: any) => {
        console.log('API response resolved:', response)
        
        activeStream = new ConversationStream(
          response,
          (chunk: any) => {
            console.log('Stream chunk received:', chunk)
            appendChunk(aiMsg, chunk)
            onScroll()
          },
          () => {
            console.log('Stream finished, aiMsg:', aiMsg)
            aiMsg.id = aiMsg.id || Date.now().toString()
            streamLoading.value = false
            activeStream = null
            onScroll()
            resolve(aiMsg)
          },
          (e: any) => {
            console.error('Stream error:', e)
            aiMsg.content.push({ type: 'FAILURE', content: String(e) })
            aiMsg.id = aiMsg.id || Date.now().toString()
            streamLoading.value = false
            activeStream = null
            reject(e)
          }
        )
        activeStream.start()
      }).catch((e: any) => {
        console.error('API call failed:', e)
        aiMsg.content.push({ type: 'FAILURE', content: String(e) })
        aiMsg.id = aiMsg.id || Date.now().toString()
        streamLoading.value = false
        reject(e)
      })
    })
  }

  const stopStream = () => {
    if (activeStream) {
      activeStream.cancel()
      activeStream = null
    }
    streamLoading.value = false
  }

  const chatRequest = (chatId: string, data: any) => {
    return api.chat(chatId, data)
  }

  const startStream = (opts: {
    cid: string
    request: () => Promise<any>
    onStream: (chunk: any) => void
    onFinish?: () => void
    onFailure?: (e: any) => void
  }) => {
    streamLoading.value = true
    opts.request().then((response: any) => {
      activeStream = new ConversationStream(
        response,
        opts.onStream,
        () => {
          streamLoading.value = false
          activeStream = null
          opts.onFinish?.()
        },
        (e: any) => {
          streamLoading.value = false
          activeStream = null
          opts.onFailure?.(e)
        },
      )
      activeStream.start()
    }).catch((e: any) => {
      streamLoading.value = false
      opts.onFailure?.(e)
    })
  }

  return {
    appInfo,
    conversations,
    currentChatId,
    currentConversation,
    messages,
    msgLoading,
    streamLoading,
    loadConversations,
    openChat,
    switchChat,
    deleteChat,
    renameChat,
    loadMessages,
    pushMessage,
    createAnswerMessage,
    getOrCreateLastAnswerMessage,
    sendMessage,
    stopStream,
    chatRequest,
    startStream,
  }
}
