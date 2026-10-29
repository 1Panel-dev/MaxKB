import type { CHAT_TYPE } from './enums'
import type { ChatApplicationProfile, ChatContent, ChatLogRecord, ChatUserProfile, Dict } from '@/api/types'

/**
 * 当前对话的智能体信息，由 view 加载并注入各组件 store，chat 与 debug 结构一致。
 * chat / portal 直接使用对话端 profile（已发布版本与访问设置）；debug 由 toDebugAppInfo 从 Admin 详情转换（当前草稿）。
 */
export type ConversationAppInfo = ChatApplicationProfile

/** 侧栏账户入口展示的当前用户，由 Chat / Debug 入口按各自的用户 Store 提供。 */
export interface ConversationAccount {
  nickName?: string
  username?: string
  token_quota?: ChatUserProfile['token_quota']
}

export interface Conversation {
  id: string
  abstract: string
  application_id?: string
  create_time?: string
  update_time?: string
}

// 助手消息底部展示数据(对话结束后 / 历史加载时填充):知识来源数、tokens、耗时、执行详情
export interface ChatRecordMeta {
  messageTokens: number
  answerTokens: number
  runTime: number
  knowledgeCount: number
  executionDetails: NonNullable<ChatLogRecord['execution_details']>
}

export interface ChatMessage {
  role: 'USER' | 'ASSISTANT'
  content: ChatContent[]
  id: string
  write_ed?: boolean
  recordId?: string // 对应后端 chat_record id(用于拉取执行详情)
  record?: ChatRecordMeta // 底部信息栏数据
}

interface StreamContentBatch {
  type?: undefined
  content?: ChatContent[]
  chat_id?: string
  chat_record_id?: string
  [key: string]: unknown
}

/** SSE 支持批量内容分片，也支持直接发送单个内容项。 */
export type StreamChunk = StreamContentBatch | ChatContent

export type ChatType = (typeof CHAT_TYPE)[keyof typeof CHAT_TYPE]

// 通用「发起/续跑一次对话」的参数。message-input、表单节点等任何能发起对话的地方共用。
export interface SendMessageOptions {
  chatId?: string // 目标会话 id;新建会话时由调用方(message-input)惰性生成后传入,缺省沿用当前已加载会话
  message: ChatContent // 后端 message dict {content,type,image_list?,...}
  newQuestion: boolean // true=新增 question(新 USER 气泡 + 新 answer 消息);false=续跑已存在的 assistant 消息
  questionContent?: ChatContent // newQuestion=true 时 USER 气泡展示的 content 项，缺省用 message
  reChat?: boolean
  formData?: Dict<unknown>
  position?: unknown
  chatRecordId?: string | null
  chunkId?: string | null
  onNext?: (chunk: StreamChunk) => void // 逐段回调
  onComplete?: (e?: unknown) => void // 结束回调:e 为空=正常结束,有值=失败
}

// 模式适配:chat / debug 只在这些 API 上有差异,由 view/{mode} 组装时注入。
export interface ConversationApiAdapter {
  pageConversations: (page: number, size: number) => Promise<{ records?: Conversation[] } | null | undefined>
  pageRecords: (chatId: string, page: number, size: number) => Promise<{ records?: ChatLogRecord[] } | null | undefined>
  recordDetail: (chatId: string, chatRecordId: string) => Promise<ChatLogRecord | null | undefined>
  remove: (chatId: string) => Promise<unknown>
  rename: (chatId: string, data: { abstract: string }) => Promise<unknown>
  chatMessage: (chatId: string, data: Dict<unknown>) => Promise<Response>
  resumeMessage: (chatId: string, chatRecordId: string) => Promise<Response>
  uploadFile: (file: File, chatId: string, onProgress?: (percent: number) => void) => Promise<string>
  cancel: (chatId: string) => Promise<unknown>
}

// 说明:各组件 store 的类型不在此集中声明,而是各组件 index.ts 用 ReturnType 自导出
// (ConversationListStore / MessageListStore / MessageInputStore / ExecutionDetailStore)。
