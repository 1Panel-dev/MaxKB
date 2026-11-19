import type { ApplicationDisplaySetting } from './application'
import type { ChatContent } from './chat-log'

/** 公开分享接口返回的问答记录。 */
export interface ChatShareRecord {
  id: string
  create_time?: string
  problem_text: string
  answer_text: string
  answer_text_list: (ChatContent | ChatContent[])[]
  /** 提问内容项 */
  question: ChatContent
  /** 回答内容项列表 */
  messages: ChatContent[]
}

export type ChatShareAppInfo = Partial<
  Pick<ApplicationDisplaySetting, 'avatar' | 'show_avatar' | 'user_avatar' | 'show_user_avatar' | 'custom_theme' | 'chat_background'>
>

export interface ChatShareDetail {
  abstract: string | null
  chat_record_list: ChatShareRecord[]
  app_info: ChatShareAppInfo
}
