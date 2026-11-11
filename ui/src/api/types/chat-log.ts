import type { CHAT_LOG_SOURCE } from '@/api/enums'
import type { Dict } from './common'
import type { DocumentResourceType } from './document'
import type { KnowledgeHitTestAsset } from './knowledge'

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
export interface ChatLogRecord extends Partial<ChatFeedback> {
  id: string
  create_time?: string
  /** 提问内容项 */
  question: ChatContent
  /** 回答内容项列表 */
  messages: ChatContent[]
  message_tokens?: number
  answer_tokens?: number
  run_time?: number
  improve_paragraph_id_list?: string[]
  paragraph_list?: ChatParagraphSource[]
  execution_details?: Dict<unknown>[]
}

/** 回答引用的知识库分段，来自检索与重排节点，仅在开启「显示知识来源」时返回。 */
export interface ChatParagraphSource {
  id: string
  title?: string
  /** 分段正文，Markdown */
  content?: string
  similarity?: number
  is_active?: boolean
  document_id?: string
  document_name?: string
  document_resource_type?: DocumentResourceType | null
  document_image_id?: string | null
  hit_asset?: KnowledgeHitTestAsset | null
  knowledge_id?: string
  knowledge_name?: string
  knowledge_type?: string
  /** 历史快照中可能为 JSON 字符串 */
  meta?: ChatParagraphSourceMeta | string | null
}

/** 分段来源文档的元数据。 */
export interface ChatParagraphSourceMeta {
  source_file_id?: string
  source_url?: string
  allow_download?: boolean
}

/** 对话反馈：-1 未评价，0 满意，1 不满意。 */
export interface ChatFeedback {
  vote_status: '-1' | '0' | '1'
  vote_reason?: 'accurate' | 'complete' | 'inaccurate' | 'incomplete' | 'other' | null
  vote_other_content?: string
}
