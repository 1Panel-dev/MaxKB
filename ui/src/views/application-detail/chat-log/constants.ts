/** 对话来源协议值对应的响应式文案。 */
import { computed, reactive } from 'vue'
import type { ChatLogSource } from '@/api/types'
import { CHAT_LOG_SOURCE } from '@/api/enums'
import { t } from '@/locales'

export const CHAT_LOG_SOURCE_LABELS: Record<ChatLogSource, string> = reactive({
  [CHAT_LOG_SOURCE.ONLINE]: computed(() => t('application.chatLog.source.online')),
  [CHAT_LOG_SOURCE.API_CALL]: computed(() => t('application.chatLog.source.apiCall')),
  [CHAT_LOG_SOURCE.ENTERPRISE_WECHAT]: computed(() => t('auth.methods.wecom')),
  [CHAT_LOG_SOURCE.WECHAT_PUBLIC_ACCOUNT]: computed(() => t('application.chatLog.source.wechatPublicAccount')),
  [CHAT_LOG_SOURCE.LARK]: computed(() => t('auth.methods.lark')),
  [CHAT_LOG_SOURCE.DINGTALK]: computed(() => t('auth.methods.dingtalk')),
  [CHAT_LOG_SOURCE.ENTERPRISE_WECHAT_ROBOT]: computed(() => t('application.chatLog.source.enterpriseWechatRobot')),
  [CHAT_LOG_SOURCE.TRIGGER]: computed(() => t('application.chatLog.source.trigger')),
  [CHAT_LOG_SOURCE.SLACK]: computed(() => t('application.access.slack.label')),
})
