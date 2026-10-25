import type { CHAT_LOG_SOURCE } from '@/api/enums'
import type { Dict } from './common'

export type ChatLogSource = (typeof CHAT_LOG_SOURCE)[keyof typeof CHAT_LOG_SOURCE]

/** 将所选对话的问答添加至目标文档。 */
export interface ChatLogAddKnowledgePayload {
  knowledge_id: string
  document_id: string
  chat_ids: string[]
}

/** 智能体对话日志列表记录。 */
export interface ChatLog {
  id: string
  abstract: string
  chat_record_count: number
  star_num: number
  trample_num: number
  mark_sum: number
  asker?: { username?: string; nick_name?: string } | null
  ip_address?: string | null
  source?: { type?: string } | null
  update_time: string
}

/** 历史消息与流式分片共用的内容项，未约定的扩展字段保留为 unknown。 */
export interface ChatContent {
  type: string
  id?: string
  content?: string
  name?: string
  status?: string
  arguments?: string
  children?: ChatContent[]
  workflowRunId?: string
  extra?: unknown
  form_field_list?: Dict<unknown>[]
  form_content_format?: string
  form_data?: Dict<unknown>
  is_submit?: boolean
  position?: unknown
  chat_record_id?: string
  [key: string]: unknown
}

/** 对话日志中的单条问答记录，仅列出前端使用的字段。 */
export interface ChatLogRecord {
  id: string
  /** 提问内容项 */
  question: ChatContent
  /** 回答内容项列表 */
  messages: ChatContent[]
  message_tokens?: number
  answer_tokens?: number
  run_time?: number
  paragraph_list?: Dict<unknown>[]
  execution_details?: Dict<unknown>[]
}
