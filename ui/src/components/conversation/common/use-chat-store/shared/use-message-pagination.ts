import { ref, type Ref } from 'vue'
import type { ChatMessage } from '../../types'

export function useMessagePagination(
  opts: {
    pageConversationMessage: (cid: string, query: any) => Promise<any>
  },
  loading: Ref<boolean> = ref(false),
) {
  const messages = ref<ChatMessage[]>([])

  const currentPage = ref(1)
  const pageSize = 20
  const hasMore = ref(true)

  const loadMessages = async (cid: string, page = 1) => {
    loading.value = true
    try {
      const res = await opts.pageConversationMessage(cid, { currentPage: page, pageSize })
      const records = (res?.records || []).reverse()
      const result = records.flatMap((record: any) => {
        return [
          {
            role: 'USER',
            content: [record.question],
            id: record.id + '_USER',
          },
          {
            role: 'ASSISTANT',
            content: record.messages,
            id: record.id + '_ASSISTANT',
          },
        ]
      })
      if (page === 1) {
        messages.value = result
      } else {
        messages.value = [...result, ...messages.value]
      }
      currentPage.value = page
      hasMore.value = records.length >= pageSize
    } catch (e) {
      // 静默处理
    } finally {
      loading.value = false
    }
  }

  const loadMoreMessages = async (cid: string) => {
    if (!hasMore.value || loading.value) return
    await loadMessages(cid, currentPage.value + 1)
  }

  const pushMessage = (msg: ChatMessage) => {
    messages.value.push(msg)
  }

  const resetMsgState = () => {
    messages.value = []
    currentPage.value = 1
    hasMore.value = true
  }

  return {
    messages,
    loading,
    hasMore,
    loadMessages,
    loadMoreMessages,
    pushMessage,
    resetMsgState,
  }
}
