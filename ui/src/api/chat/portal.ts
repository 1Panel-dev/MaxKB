/** 提供门户的智能体与历史对话接口。 */

import { get } from './core/request'
import type { ResponsePage } from './core/types'
import type { ChatApplicationProfile, PortalApplicationConversations } from '@/api/types'

/** 分页获取门户可访问的智能体，支持按名称搜索。 */
const getPortalApplicationPage = (page: number, size: number, name?: string) => {
  return get<ResponsePage<ChatApplicationProfile>>(`/v3/portal/application/${page}/${size}`, name ? { name } : undefined)
}

/** 分页获取门户可访问的智能体及各自最近的历史对话。 */
const getPortalConversationPage = (page: number, size: number) => {
  return get<ResponsePage<PortalApplicationConversations>>(`/v3/portal/chat/${page}/${size}`)
}

export default { getPortalApplicationPage, getPortalConversationPage }
