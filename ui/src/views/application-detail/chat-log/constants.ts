import { CHAT_LOG_SOURCE } from '@/api/enums'
import type { ChatLogSource } from '@/api/types'

export const CHAT_LOG_SOURCE_LABELS: Record<ChatLogSource, string> = {
  [CHAT_LOG_SOURCE.ONLINE]: '线上使用',
  [CHAT_LOG_SOURCE.API_CALL]: 'API 调用',
  [CHAT_LOG_SOURCE.ENTERPRISE_WECHAT]: '企业微信',
  [CHAT_LOG_SOURCE.WECHAT_PUBLIC_ACCOUNT]: '微信公众号',
  [CHAT_LOG_SOURCE.LARK]: '飞书',
  [CHAT_LOG_SOURCE.DINGTALK]: '钉钉',
  [CHAT_LOG_SOURCE.ENTERPRISE_WECHAT_ROBOT]: '企业微信机器人',
  [CHAT_LOG_SOURCE.TRIGGER]: '触发器',
  [CHAT_LOG_SOURCE.SLACK]: 'Slack',
}
