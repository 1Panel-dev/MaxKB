import type { ChatContent } from './chat-log'
import type { Dict } from './common'

/** 公开分享接口返回的旧版问答记录。 */
export interface ChatShareRecord {
  id: string
  problem_text: string
  answer_text: string
  answer_text_list: (ChatContent | ChatContent[])[]
  execution_details?: Dict<unknown>[]
}

export interface ChatShareDetail {
  abstract: string | null
  chat_record_list: ChatShareRecord[]
}
