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

/** 对话日志中的单条问答记录，仅列出前端使用的字段。 */
export interface ChatLogRecord {
  id: string
  /** 提问内容项 */
  question: Dict<unknown>
  /** 回答内容项列表 */
  messages: Dict<unknown>[]
  message_tokens?: number
  answer_tokens?: number
  run_time?: number
  paragraph_list?: Dict<unknown>[]
  execution_details?: Dict<unknown>[]
}
