import { CHAT_TYPE } from '@/conversation-panel/common/enums'
import AdminConversationApi from '@/api/admin/workspace/conversation'
import ConversationApi from '@/api/chat/conversation'
import type { ChatType } from './types'

/** 根据面板模式选择对话接口。 */
export function getApi(type: ChatType) {
  return type === CHAT_TYPE.DEBUG ? AdminConversationApi : ConversationApi
}
