import { ref, inject, type InjectionKey } from 'vue'
import type { ChatLogRecord } from '@/api/types'
import type { ChatMessage, ChatRecordMeta } from '../../core/types'

// 只读会话记录(如对话日志):只分页拉取历史记录,不发送、不续跑、不流式。
// 与 message-list 刻意不共用 store 约定,也不注入 MESSAGE_LIST_KEY,表单等内容项因此自动只读。
export interface LogMessageListDeps {
  pageRecords: (chatId: string, page: number, size: number) => Promise<{ records: ChatLogRecord[] }>
  getChatId: () => string
}

// 从后端 chat_record(reset_chat_record 结构)提取底部信息栏数据
const buildRecordMeta = (raw: ChatLogRecord): ChatRecordMeta => ({
  messageTokens: raw.message_tokens || 0,
  answerTokens: raw.answer_tokens || 0,
  runTime: raw.run_time || 0,
  knowledgeCount: (raw.paragraph_list || []).length,
  executionDetails: raw.execution_details || [],
})

export function createLogMessageListStore(deps: LogMessageListDeps) {
  const { pageRecords, getChatId } = deps

  const messages = ref<ChatMessage[]>([])
  const loading = ref(false)

  const pageSize = 20
  const currentPage = ref(1)
  const hasMore = ref(true)

  // 接口按最新在前分页:页内 reverse 成正序,更旧的页拼到前面
  const loadMessages = async (cid: string, page = 1) => {
    loading.value = true
    try {
      const res = await pageRecords(cid, page, pageSize)
      const records = [...(res?.records || [])].reverse()
      const result = records.flatMap((record): ChatMessage[] => [
        { role: 'USER', content: [record.question], id: record.id + '_USER' },
        {
          role: 'ASSISTANT',
          content: record.messages,
          id: record.id + '_ASSISTANT',
          recordId: record.id,
          record: buildRecordMeta(record),
        },
      ])
      messages.value = page === 1 ? result : [...result, ...messages.value]
      currentPage.value = page
      hasMore.value = records.length >= pageSize
    } catch {
      // 静默处理
    } finally {
      loading.value = false
    }
  }

  // 切换记录时由使用方主动调用。先清空再拉:无消息时的 loading 即首页加载
  const load = async () => {
    const cid = getChatId()
    messages.value = []
    currentPage.value = 1
    hasMore.value = true
    if (!cid) return
    await loadMessages(cid, 1)
  }

  const loadMore = async () => {
    const cid = getChatId()
    if (!hasMore.value || loading.value || !cid) return
    await loadMessages(cid, currentPage.value + 1)
  }

  return { messages, loading, hasMore, load, loadMore }
}

export type LogMessageListStore = ReturnType<typeof createLogMessageListStore>

export const LOG_MESSAGE_LIST_KEY: InjectionKey<LogMessageListStore> = Symbol('log-message-list')

export function useLogMessageListStore(): LogMessageListStore {
  const store = inject(LOG_MESSAGE_LIST_KEY)
  if (!store) throw new Error('useLogMessageListStore 必须在提供 LOG_MESSAGE_LIST_KEY 的视图内使用')
  return store
}
