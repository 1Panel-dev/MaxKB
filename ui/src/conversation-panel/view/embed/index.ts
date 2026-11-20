import type { ChatConversationBundle, ChatConversationRouting } from '../chat/index'
import { createChatConversation } from '../chat/index'

/**
 * embed 模式：第三方页面通过嵌入脚本以 iframe 打开 `/:accessToken/?mode=embed`。
 * 接口、会话与地址同步均与单应用 chat 模式一致，仅头部不同，因此直接复用 chat 装配。
 */
export function createEmbedConversation(routing?: ChatConversationRouting): ChatConversationBundle {
  return createChatConversation(routing)
}
