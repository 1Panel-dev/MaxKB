import { ref, inject, type InjectionKey } from 'vue'
import { nanoid } from 'nanoid'
import { aggregators } from '../../core/aggregators'
import { ConversationStream } from '../../core/stream'
import type { ChatMessage, ChatRecordMeta, SendMessageOptions } from '../../core/types'

export interface MessageListDeps {
  pageRecords: (chatId: string, page: number, size: number) => Promise<any>
  recordDetail: (chatId: string, chatRecordId: string) => Promise<any>
  chatMessage: (chatId: string, data: any) => Promise<Response>
  resumeMessage: (chatId: string, chatRecordId: string) => Promise<Response>
  cancel: (chatId: string) => Promise<any>
  uploadFile: (file: File, chatId: string) => Promise<string>
  // 只读获取当前会话 id(单一数据源在 conversation-list)。必须无副作用:不可惰性创建,
  // 否则无会话时的 stop/cancel/loadMore 会凭空生成 id 并误请求后端。
  getChatId: () => string
}

// 从后端 chat_record(分页项或详情接口,均为 reset_chat_record 结构)提取底部信息栏数据
const buildRecordMeta = (raw: any): ChatRecordMeta => ({
  messageTokens: raw?.message_tokens || 0,
  answerTokens: raw?.answer_tokens || 0,
  runTime: raw?.run_time || 0,
  knowledgeCount: (raw?.paragraph_list || []).length,
  executionDetails: raw?.execution_details || [],
})

export function createMessageListStore(deps: MessageListDeps) {
  const { pageRecords, recordDetail, chatMessage, resumeMessage, cancel: cancelApi, uploadFile, getChatId } = deps

  const messages = ref<ChatMessage[]>([])
  const loading = ref(false)

  // ── 分页 ─────────────────────────────────────────────
  const pageSize = 20
  const currentPage = ref(1)
  const hasMore = ref(true)

  const loadMessages = async (cid: string, page = 1) => {
    loading.value = true
    try {
      const res = await pageRecords(cid, page, pageSize)
      const records = (res?.records || []).reverse()
      const result = records.flatMap((record: any) => [
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
    } catch (e) {
      // 静默处理
    } finally {
      loading.value = false
    }
  }

  const loadMore = async () => {
    const cid = getChatId()
    if (!hasMore.value || loading.value || !cid) return
    await loadMessages(cid, currentPage.value + 1)
  }

  const resetMessages = () => {
    messages.value = []
    currentPage.value = 1
    hasMore.value = true
  }

  // 对话结束后拉取该条记录详情,填充底部信息栏(tokens/耗时/知识来源/执行详情)
  const getChatRecord = async (target: any, cid: string) => {
    const rid = target?.recordId
    if (!cid || !rid) return
    try {
      target.record = buildRecordMeta(await recordDetail(cid, rid))
    } catch {
      /* 底部信息栏拉取失败不影响对话 */
    }
  }

  // ── 流式聚合 ─────────────────────────────────────────
  const appendChunk = (message: ChatMessage, chunk: any) => {
    if (!chunk) return
    const contentArray = Array.isArray(chunk.content) ? chunk.content : chunk.type ? [chunk] : null
    if (!contentArray) return
    contentArray.forEach((item: any) => {
      if (!item?.type) return
      const aggregator = aggregators[item.type]
      if (!aggregator) return
      const index = message.content.findIndex((c: any) => c.id === item.id && c.type === item.type)
      if (index >= 0) message.content[index] = aggregator(message.content[index], item)
      else message.content.push(aggregator({}, item))
    })
  }

  // ── 流生命周期 + 进度订阅 ────────────────────────────
  let currentStream: ConversationStream | null = null
  const closeStream = () => {
    if (currentStream) {
      currentStream.cancel()
      currentStream = null
      return true
    }
    return false
  }

  const progressListeners = new Set<() => void>()
  const onStreamProgress = (fn: () => void) => {
    progressListeners.add(fn)
    return () => progressListeners.delete(fn)
  }
  const emitProgress = () =>
    progressListeners.forEach((fn) => {
      try {
        fn()
      } catch {
        /* 单个订阅者异常不影响其他 */
      }
    })

  // onNext 逐段回调,onComplete(e?) 结束回调:e 为空表示正常结束,有值表示失败
  const runStream = (
    request: () => Promise<Response>,
    onNext: (chunk: any) => void,
    onComplete: (e?: any) => void,
  ) => {
    closeStream()
    request()
      .then((response: any) => {
        currentStream = new ConversationStream(
          response,
          (chunk: any) => {
            onNext(chunk)
            emitProgress()
          },
          (e) => {
            currentStream = null
            onComplete(e)
          },
        )
        currentStream.start()
      })
      .catch((e) => onComplete(e ?? new Error('stream request failed')))
  }

  // ── 发送 / 续跑 ─────────────────────────────────────
  const sendMessage = (opts: SendMessageOptions) => {
    // 新建会话由调用方(message-input)惰性生成后传入 chatId;表单续跑等缺省沿用当前会话
    const cid = opts.chatId || getChatId()
    if (!cid) return

    let target: any
    if (opts.newQuestion) {
      messages.value.push({ role: 'USER', content: [opts.questionContent ?? opts.message], id: nanoid() })
      messages.value.push({ role: 'ASSISTANT', content: [], id: '' })
      target = messages.value[messages.value.length - 1]
    } else {
      target =
        messages.value.find((m: any) => m.id === `${opts.chatRecordId}_ASSISTANT`) ||
        messages.value[messages.value.length - 1]
    }
    if (!target) return

    const payload: any = { message: opts.message, stream: true, re_chat: opts.reChat ?? false }
    if (opts.formData) payload.form_data = opts.formData
    if (opts.position !== undefined) payload.position = opts.position
    if (opts.chatRecordId) payload.chat_record_id = opts.chatRecordId
    if (opts.chunkId) payload.chunk_id = opts.chunkId

    loading.value = true
    runStream(
      () => chatMessage(cid, payload),
      (chunk) => {
        if (chunk?.chat_record_id && !target.recordId) target.recordId = chunk.chat_record_id
        appendChunk(target, chunk)
        opts.onNext?.(chunk)
      },
      (e) => {
        target.write_ed = true
        loading.value = false
        if (!e) getChatRecord(target, cid)
        opts.onComplete?.(e)
      },
    )
  }

  // 优雅停止:仅通知后端取消,本地流继续读到 [DONE] 自行结束
  const stop = () => {
    const cid = getChatId()
    if (!currentStream || !cid) return
    cancelApi(cid).catch(() => { })
  }
  // 硬取消:卸载/离开时断开本地流并通知后端
  const cancel = () => {
    const cid = getChatId()
    if (closeStream() && cid) cancelApi(cid).catch(() => { })
  }

  // ── 切换会话:由 conversation-list 主动调用(list 先写好 currentChatId 再调本函数)──
  const load = async () => {
    const cid = getChatId()
    closeStream()
    if (!cid) {
      resetMessages()
      return
    }
    await loadMessages(cid, 1)
    const lastMsg = messages.value[messages.value.length - 1]
    if (!lastMsg || (lastMsg.content && lastMsg.content.length > 0)) return
    loading.value = true
    const recordId = lastMsg.id.replace('_USER', '').replace('_ASSISTANT', '')
    runStream(
      () => resumeMessage(cid, recordId),
      (chunk) => {
        const m = messages.value[messages.value.length - 1]
        if (m) appendChunk(m, chunk)
      },
      (e) => {
        if (!e) {
          const m = messages.value[messages.value.length - 1]
          if (m) {
            m.write_ed = true
            if (!m.recordId) m.recordId = recordId
            getChatRecord(m, cid)
          }
        }
        loading.value = false
      },
    )
  }

  return {
    messages,
    loading,
    hasMore,
    load,
    loadMore,
    sendMessage,
    uploadFile,
    onStreamProgress,
    stop,
    cancel,
  }
}

export type MessageListStore = ReturnType<typeof createMessageListStore>

export const MESSAGE_LIST_KEY: InjectionKey<MessageListStore> = Symbol('message-list')

export function useMessageListStore(): MessageListStore {
  const store = inject(MESSAGE_LIST_KEY)
  if (!store) throw new Error('useMessageListStore 必须在 ConversationView 内使用')
  return store
}

// 供“只显示”等场景可选注入:拿不到返回 null(如 form 在无发送能力时降级只读)
export function useMessageListStoreOptional(): MessageListStore | null {
  return inject(MESSAGE_LIST_KEY, null)
}
