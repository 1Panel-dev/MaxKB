/** 对话端智能体信息类型。 */

import type LogicFlow from '@logicflow/core'
import type { ApplicationType } from './application'
import type { Dict } from './common'

/**
 * 对话端可见的智能体信息。门户智能体列表只返回基础字段；
 * profile 接口额外返回对话配置（已发布版本）与访问设置，访问设置中的展示项需许可证有效才返回。
 */
export interface ChatApplicationProfile {
  id: string
  name: string
  icon: string
  desc?: string | null
  prologue?: string
  type?: ApplicationType
  dialogue_number?: number
  problem_optimization?: boolean
  stt_model_id?: string | null
  tts_model_id?: string | null
  stt_model_enable?: boolean
  tts_model_enable?: boolean
  tts_type?: string
  tts_autoplay?: boolean
  stt_autosend?: boolean
  file_upload_enable?: boolean
  file_upload_setting?: Dict<unknown>
  /** 仅包含开始节点（base-node），非工作流智能体为 null。 */
  work_flow?: LogicFlow.GraphConfigData | null
  show_source?: boolean
  show_exec?: boolean
  show_share?: boolean
  language?: string | null
  show_history?: boolean
  draggable?: boolean
  show_guide?: boolean
  avatar?: string
  show_avatar?: boolean
  float_icon?: string
  disclaimer?: boolean
  disclaimer_value?: string
  custom_theme?: { theme_color?: string; header_font_color?: string }
  user_avatar?: string
  show_user_avatar?: boolean
  float_location?: Dict<unknown>
  chat_background?: string
}

/** 门户历史对话中单条会话的摘要。 */
export interface PortalConversationSummary {
  id: string
  abstract: string
  create_time: string
  update_time: string
}

/** 门户历史对话按智能体分组，每个智能体最多返回最近 5 条会话；未开启历史记录的智能体不返回会话。 */
export interface PortalApplicationConversations {
  id: string
  name: string
  icon: string
  conversations: PortalConversationSummary[]
  count: number
}
