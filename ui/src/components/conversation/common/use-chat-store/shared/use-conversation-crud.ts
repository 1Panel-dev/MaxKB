import { ref } from 'vue'
import type { Conversation } from '../../types'

export function useConversationCrud(opts: {
  pageConversationAPI: (query: any) => Promise<any>
}) {
  const conversations = ref<Conversation[]>([])
  const currentPage = ref(1)
  const pageSize = 50
  const hasMore = ref(true)
  const loading = ref(false)

  const loadConversations = async (page = 1) => {
    loading.value = true
    try {
      const res = await opts.pageConversationAPI({ currentPage: page, pageSize })
      const records = res.data?.records || []
      if (page === 1) {
        conversations.value = records
      } else {
        conversations.value = [...conversations.value, ...records]
      }
      currentPage.value = page
      hasMore.value = records.length >= pageSize
    } catch (e) {
      // debug 模式下历史接口可能不存在，静默处理
    } finally {
      loading.value = false
    }
  }

  const loadMore = async () => {
    if (!hasMore.value || loading.value) return
    await loadConversations(currentPage.value + 1)
  }

  return {
    conversations,
    loading,
    hasMore,
    loadConversations,
    loadMore,
  }
}
