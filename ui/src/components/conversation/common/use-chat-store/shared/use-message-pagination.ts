import { ref } from 'vue'
import type { ChatMessage } from '../../types'

export function useMessagePagination(opts: {
  pageConversationMessage: (cid: string, query: any) => Promise<any>
}) {
  const messages = ref<ChatMessage[]>([])
  const msgLoading = ref(false)
  const currentPage = ref(1)
  const pageSize = 20
  const hasMore = ref(true)

  const loadMessages = async (cid: string, page = 1) => {
    msgLoading.value = true
    try {
      const res = await opts.pageConversationMessage(cid, { currentPage: page, pageSize })
      const records = res.data?.records || []
      const result: ChatMessage[] = []
      records.forEach((record: any) => {
        // 将 question 和 messages 平铺成一个数组
        const contentList: any[] = []
        
        // 添加 question
        if (record.question) {
          contentList.push(record.question)
        } else if (record.problem_text) {
          contentList.push({ type: 'QUESTION', content: record.problem_text })
        }
        
        // 添加 messages
        if (record.messages && Array.isArray(record.messages)) {
          contentList.push(...record.messages)
        } else if (record.answer_text_list) {
          contentList.push(...record.answer_text_list.flat())
        }
        
        if (contentList.length > 0) {
          result.push({
            id: record.id,
            role: 'USER',
            content: contentList,
            write_ed: true,
          })
        }
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
      msgLoading.value = false
    }
  }

  const loadMoreMessages = async (cid: string) => {
    if (!hasMore.value || msgLoading.value) return
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
    msgLoading,
    hasMore,
    loadMessages,
    loadMoreMessages,
    pushMessage,
    resetMsgState,
  }
}
