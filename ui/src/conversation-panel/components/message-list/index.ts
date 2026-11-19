import { computed, inject, ref, shallowRef } from 'vue'
import { nanoid } from 'nanoid'
import type { TextToSpeech } from '../../core/speech'
import type { ChatMessage, ChatRecordMeta, ConversationApiAdapter, ConversationAppInfo, SendMessageOptions, StreamChunk } from '../../core/types'
import type { ChatFeedback, ChatLogRecord, Dict } from '@/api/types'
import type { InjectionKey, Ref } from 'vue'
import { aggregators } from '../../core/aggregators'
import { StreamSpeech, isSpeechSupported } from '../../core/speech'
import { ConversationStream } from '../../core/stream'

export interface MessageListDeps extends Pick<
  ConversationApiAdapter,
  'feedback' | 'pageRecords' | 'recordDetail' | 'chatMessage' | 'resumeMessage' | 'cancel' | 'truncate' | 'uploadFile'
> {
  // 只读获取当前会话 id(单一数据源在 conversation-list)。必须无副作用:不可惰性创建,
  // 否则无会话时的 stop/cancel/loadMore 会凭空生成 id 并误请求后端。
  getChatId: () => string
  /** 当前智能体信息：只读，由 view 加载维护。 */
  appInfo: Readonly<Ref<ConversationAppInfo | null>>
  /** 按智能体的语音播放设置自动朗读流式回答，仅 Chat、门户对话开启。 */
  speechAutoplay?: boolean
  /** 模型语音合成；智能体选择浏览器语音或未提供时使用浏览器语音。 */
  textToSpeech?: TextToSpeech
}

// 从后端 chat_record(分页项或详情接口,均为 reset_chat_record 结构)提取底部信息栏数据
const buildRecordMeta = (raw?: ChatLogRecord | null): ChatRecordMeta => ({
  feedback: { vote_status: raw?.vote_status ?? '-1', vote_reason: raw?.vote_reason, vote_other_content: raw?.vote_other_content },
  createTime: raw?.create_time,
  messageTokens: raw?.message_tokens || 0,
  answerTokens: raw?.answer_tokens || 0,
  runTime: raw?.run_time || 0,
  paragraphList: raw?.paragraph_list || [],
  executionDetails: raw?.execution_details || [],
})

/** 每条消息所属问答轮次的记录 ID：提问取紧随其后那条回答的记录 ID；回答尚未返回记录 ID 时为 undefined。 */
export const getMessageRecordIds = (messages: ChatMessage[]) =>
  messages.map((message, index) => (message.role === 'ASSISTANT' ? message.recordId : messages[index + 1]?.recordId))

export function createMessageListStore(deps: MessageListDeps) {
  const { pageRecords, recordDetail, chatMessage, resumeMessage, cancel: cancelApi, truncate: truncateApi, uploadFile, getChatId, appInfo } = deps

  const messages = ref<ChatMessage[]>([])
  const messageRecordIds = computed(() => getMessageRecordIds(messages.value))
  const loading = ref(false)
  const streamLoading = ref(false)

  // ── 分页 ─────────────────────────────────────────────
  const pageSize = 30
  const currentPage = ref(1)
  const hasMore = ref(false)

  const loadMessages = async (cid: string, page = 1) => {
    loading.value = true
    try {
      const res = await pageRecords(cid, page, pageSize)
      const records = (res?.records || []).reverse()
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
      return records.length > 0
    } catch {
      // 静默处理
      return false
    } finally {
      loading.value = false
    }
  }

  const loadMore = async (): Promise<boolean> => {
    const cid = getChatId()
    if (!hasMore.value || loading.value || !cid) return false
    return loadMessages(cid, currentPage.value + 1)
  }

  const resetMessages = () => {
    messages.value = []
    currentPage.value = 1
    hasMore.value = false
  }

  // 截断会话：后端删除该记录及之后的记录成功后，同步移除该轮提问起的全部消息；请求失败时保留现有消息
  // 截断请求期间不允许发起对话（重新生成、表单续跑等），避免操作即将被删除的记录
  let truncating = false
  const truncateFrom = async (chatRecordId: string) => {
    const cid = getChatId()
    if (!cid || truncating) return
    truncating = true
    try {
      await truncateApi(cid, chatRecordId)
    } finally {
      truncating = false
    }
    // 请求期间切换了会话时，当前列表已不是被截断的会话
    if (cid !== getChatId()) return
    const answerIndex = messages.value.findIndex((message) => message.recordId === chatRecordId)
    if (answerIndex < 0) return
    const questionIndex = messages.value[answerIndex - 1]?.role === 'USER' ? answerIndex - 1 : answerIndex
    messages.value.splice(questionIndex)
  }

  // 对话结束后拉取该条记录详情,填充底部信息栏(tokens/耗时/知识来源/执行详情)
  const getChatRecord = async (target: ChatMessage, cid: string) => {
    const rid = target?.recordId
    if (!cid || !rid) return
    try {
      target.record = buildRecordMeta(await recordDetail(cid, rid))
    } catch {
      /* 底部信息栏拉取失败不影响对话 */
    }
  }

  // ── 流式聚合 ─────────────────────────────────────────
  const appendChunk = (message: ChatMessage, chunk: StreamChunk) => {
    if (!chunk) return
    const contentArray = Array.isArray(chunk.content) ? chunk.content : chunk.type ? [chunk] : null
    if (!contentArray) return
    contentArray.forEach((item) => {
      if (!item?.type) return
      const aggregator = aggregators[item.type]
      if (!aggregator) return
      const index = message.content.findIndex((content) => content.id === item.id && content.type === item.type)
      if (index >= 0) message.content[index] = aggregator(message.content[index], item)
      else message.content.push(aggregator({}, item))
    })
  }

  // ── 流生命周期 + 进度订阅 ────────────────────────────
  let currentStream: ConversationStream | null = null
  const closeStream = () => {
    if (currentStream) {
      // 主动取消的流不会回调 onComplete,需在此复位对话加载
      currentStream.cancel()
      currentStream = null
      streamLoading.value = false
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
  const runStream = (request: () => Promise<Response>, onNext: (chunk: StreamChunk) => void, onComplete: (e?: unknown) => void) => {
    closeStream()
    streamLoading.value = true
    request()
      .then((response) => {
        currentStream = new ConversationStream(
          response,
          (chunk: StreamChunk) => {
            onNext(chunk)
            emitProgress()
          },
          (e) => {
            currentStream = null
            streamLoading.value = false
            onComplete(e)
          },
        )
        currentStream.start()
      })
      .catch((e) => {
        streamLoading.value = false
        onComplete(e ?? new Error('stream request failed'))
      })
  }

  // ── 朗读 ─────────────────────────────────────────────
  // 同一时间只朗读一条回答：底部栏手动朗读整条回答；开启自动播放时每次发送新建朗读，由 onNext 累积正文增量。
  // 暂停保留进度，再次继续从断点朗读；读别的回答、新发送、切换会话、离开或读完时丢弃。
  // 智能体选择模型语音且提供合成接口时调用接口，否则使用浏览器语音。
  let streamSpeech: StreamSpeech | null = null
  /** 正在朗读（含暂停）的回答，供底部栏显示朗读状态。 */
  const speakingMessage = shallowRef<ChatMessage | null>(null)
  const speechPaused = ref(false)
  const speechTextToSpeech = computed(() => {
    const ttsType = appInfo.value?.tts_type
    return ttsType && ttsType !== 'BROWSER' ? deps.textToSpeech : undefined
  })
  const speechSupported = computed(() => isSpeechSupported(speechTextToSpeech.value))
  const stopSpeech = () => streamSpeech?.stop()
  const pauseSpeech = () => streamSpeech?.pause()
  const resumeSpeech = () => streamSpeech?.resume()
  const createSpeech = (message: ChatMessage) => {
    stopSpeech()
    if (!speechSupported.value) return null
    const speech = new StreamSpeech(speechTextToSpeech.value, (state) => {
      if (streamSpeech !== speech) return
      speechPaused.value = state === 'paused'
      if (state !== 'ended') return
      streamSpeech = null
      speakingMessage.value = null
    })
    streamSpeech = speech
    speakingMessage.value = message
    speechPaused.value = false
    return speech
  }
  const startSpeech = (message: ChatMessage) => {
    const info = appInfo.value
    if (!deps.speechAutoplay || !info?.tts_model_enable || !info.tts_autoplay) {
      stopSpeech()
      return null
    }
    return createSpeech(message)
  }
  /** 朗读整条回答正文。 */
  const playSpeech = (message: ChatMessage, text: string) => {
    const speech = createSpeech(message)
    speech?.appendText('', text)
    speech?.finish()
  }

  // ── 发送 / 续跑 ─────────────────────────────────────
  const sendMessage = (opts: SendMessageOptions) => {
    // 新建会话由调用方(message-input)惰性生成后传入 chatId;表单续跑等缺省沿用当前会话
    const cid = opts.chatId || getChatId()
    if (!cid || truncating) return

    if (opts.newQuestion) {
      messages.value.push({ role: 'USER', content: [opts.questionContent ?? opts.message], id: nanoid() })
      messages.value.push({ role: 'ASSISTANT', content: [], id: '' })
    }
    const target = opts.newQuestion
      ? messages.value[messages.value.length - 1]
      : messages.value.find(
          (message) => (!!opts.chatRecordId && message.recordId === opts.chatRecordId) || message.id === `${opts.chatRecordId}_ASSISTANT`,
        ) || messages.value[messages.value.length - 1]
    if (!target) return

    const payload: Dict<unknown> = { message: opts.message, stream: true, re_chat: opts.reChat ?? false }
    if (opts.formData) payload.form_data = opts.formData
    if (opts.position !== undefined) payload.position = opts.position
    if (opts.chatRecordId) payload.chat_record_id = opts.chatRecordId
    if (opts.chunkId) payload.chunk_id = opts.chunkId

    let replacementStarted = false
    const speech = startSpeech(target)
    runStream(
      () => chatMessage(cid, payload),
      (chunk) => {
        if (chunk?.chat_record_id && !target.recordId) target.recordId = chunk.chat_record_id
        if (opts.reChat && !replacementStarted) {
          target.content = []
          target.record = undefined
          target.write_ed = false
          replacementStarted = true
        }
        appendChunk(target, chunk)
        speech?.appendChunk(chunk)
        opts.onNext?.(chunk)
      },
      (e) => {
        // 正常结束或失败都读完已收到的内容
        speech?.finish()
        target.write_ed = true
        if (!e) getChatRecord(target, cid)
        opts.onComplete?.(e)
      },
    )
  }

  // 原回答保留到重新生成收到首个分片，避免请求失败时丢失已展示内容。
  const regenerate = (message: ChatMessage) => {
    if (streamLoading.value || loading.value || !message.recordId) return
    const index = messages.value.indexOf(message)
    const question = messages.value[index - 1]
    if (index < 1 || question?.role !== 'USER' || !question.content[0]) return
    sendMessage({ message: question.content[0], newQuestion: false, reChat: true, chatRecordId: message.recordId })
  }

  // 优雅停止:仅通知后端取消,本地流继续读到 [DONE] 自行结束
  const stop = () => {
    const cid = getChatId()
    if (!currentStream || !cid) return
    cancelApi(cid).catch(() => {})
  }
  // 硬取消:卸载/离开时断开本地流并通知后端
  const cancel = () => {
    stopSpeech()
    const cid = getChatId()
    if (closeStream() && cid) cancelApi(cid).catch(() => {})
  }

  // ── 切换会话:由 conversation-list 主动调用(list 先写好 currentChatId 再调本函数)──
  // 先清空再拉:无消息时的 loading 即首页加载(整块遮罩),有消息时的 loading 即加载更多
  const load = async () => {
    const cid = getChatId()
    stopSpeech()
    closeStream()
    resetMessages()
    if (!cid) return
    await loadMessages(cid, 1)
    const lastMsg = messages.value[messages.value.length - 1]
    if (!lastMsg || (lastMsg.content && lastMsg.content.length > 0)) return
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
      },
    )
  }

  return {
    feedback: deps.feedback ? (recordId: string, data: ChatFeedback) => deps.feedback!(getChatId(), recordId, data) : undefined,
    appInfo,
    // computed 保持消息对象原引用，供底部栏按引用比较
    speakingMessage: computed(() => speakingMessage.value),
    speechPaused: computed(() => speechPaused.value),
    speechSupported,
    playSpeech,
    pauseSpeech,
    resumeSpeech,
    stopSpeech,
    messages,
    messageRecordIds,
    loading,
    streamLoading,
    hasMore,
    load,
    loadMore,
    truncateFrom,
    sendMessage,
    regenerate,
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

/** 消息所属问答轮次的记录 ID，由消息列表逐行提供给消息内容，供内容项的编辑、分享等入口定位所属轮次。 */
export const MESSAGE_RECORD_ID_KEY: InjectionKey<Readonly<Ref<string | undefined>>> = Symbol('message-record-id')

/** 未提供时（日志等不经消息列表渲染的视图）为 undefined。 */
export function useMessageRecordId(): Readonly<Ref<string | undefined>> {
  return inject(MESSAGE_RECORD_ID_KEY, ref(undefined))
}

// 通用发送能力，由消息列表或外部宿主（如工具调试结果抽屉）提供；内容项按自身场景组装参数。
export type SendMessage = (opts: SendMessageOptions) => void

// 值为 null 表示当前不可发送（分享、执行中等），由提供方按自身状态决定
export const SEND_MESSAGE_KEY: InjectionKey<Readonly<Ref<SendMessage | null>>> = Symbol('send-message')

// 未提供时恒为 null，内容项降级只读
export function useSendMessageOptional(): Readonly<Ref<SendMessage | null>> {
  return inject(SEND_MESSAGE_KEY, ref(null))
}
