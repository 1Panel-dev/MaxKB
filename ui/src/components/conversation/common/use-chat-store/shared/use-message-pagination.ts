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
        result.push({
          id: record.id,
          role: 'USER',
          content: [{ type: 'QUESTION', content: record.problem_text }],
        })
        if (record.answer_text_list) {
          result.push({
            id: record.id + '-answer',
            role: 'ASSISTANT',
            content: record.answer_text_list.flat(),
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
