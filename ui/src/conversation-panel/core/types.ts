import type { CHAT_TYPE } from './enums'

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
  executionDetails: any[]
}

export interface ChatMessage {
  role: 'USER' | 'ASSISTANT'
  content: any[]
  id: string
  write_ed?: boolean
  recordId?: string // 对应后端 chat_record id(用于拉取执行详情)
  record?: ChatRecordMeta // 底部信息栏数据
}

export interface StreamChunk {
  content?: any[]
  chat_id?: string
  chat_record_id?: string
  [key: string]: any
}

export type ChatType = (typeof CHAT_TYPE)[keyof typeof CHAT_TYPE]

// 通用「发起/续跑一次对话」的参数。message-input、表单节点等任何能发起对话的地方共用。
export interface SendMessageOptions {
  chatId?: string // 目标会话 id;新建会话时由调用方(message-input)惰性生成后传入,缺省沿用当前已加载会话
  message: any // 后端 message dict {content,type,image_list?,...}
  newQuestion: boolean // true=新增 question(新 USER 气泡 + 新 answer 消息);false=续跑已存在的 assistant 消息
  questionContent?: any // newQuestion=true 时 USER 气泡展示的 content 项，缺省用 message
  reChat?: boolean
  formData?: Record<string, any>
  position?: any
  chatRecordId?: string | null
  chunkId?: string | null
  onNext?: (chunk: any) => void // 逐段回调
  onComplete?: (e?: any) => void // 结束回调:e 为空=正常结束,有值=失败
}

// 模式适配:chat / debug 只在这些 API 上有差异,由 view/{mode} 组装时注入。
export interface ConversationApiAdapter {
  pageConversations: (page: number, size: number) => Promise<any>
  pageRecords: (chatId: string, page: number, size: number) => Promise<any>
  recordDetail: (chatId: string, chatRecordId: string) => Promise<any>
  remove: (chatId: string) => Promise<any>
  rename: (chatId: string, data: { abstract: string }) => Promise<any>
  chatMessage: (chatId: string, data: any) => Promise<Response>
  resumeMessage: (chatId: string, chatRecordId: string) => Promise<Response>
  uploadFile: (file: File, chatId: string) => Promise<string>
  cancel: (chatId: string) => Promise<any>
}

// 说明:各组件 store 的类型不在此集中声明,而是各组件 index.ts 用 ReturnType 自导出
// (ConversationListStore / MessageListStore / MessageInputStore / ExecutionDetailStore)。
