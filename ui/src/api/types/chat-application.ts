/** 对话端智能体信息类型。 */

/** 对话端可见的智能体基础信息，仅声明当前使用的字段。 */
export interface ChatApplicationProfile {
  id: string
  name: string
  icon: string
  desc?: string
  prologue?: string
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
}
