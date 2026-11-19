/** 对话来源协议值对应的展示文案 key。 */
import type { ChatLogSource } from '@/api/types'
import { CHAT_LOG_SOURCE } from '@/api/enums'

export const CHAT_LOG_SOURCE_MESSAGE_KEYS: Record<ChatLogSource, string> = {
  [CHAT_LOG_SOURCE.ONLINE]: 'application.chatLog.source.online',
  [CHAT_LOG_SOURCE.API_CALL]: 'application.chatLog.source.apiCall',
  [CHAT_LOG_SOURCE.ENTERPRISE_WECHAT]: 'auth.methods.wecom',
  [CHAT_LOG_SOURCE.WECHAT_PUBLIC_ACCOUNT]: 'application.chatLog.source.wechatPublicAccount',
  [CHAT_LOG_SOURCE.LARK]: 'auth.methods.lark',
  [CHAT_LOG_SOURCE.DINGTALK]: 'auth.methods.dingtalk',
  [CHAT_LOG_SOURCE.ENTERPRISE_WECHAT_ROBOT]: 'application.chatLog.source.enterpriseWechatRobot',
  [CHAT_LOG_SOURCE.TRIGGER]: 'application.chatLog.source.trigger',
  [CHAT_LOG_SOURCE.SLACK]: 'application.access.slack.label',
}
