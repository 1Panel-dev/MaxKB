/** 对话日志的智能体信息：由 Admin 智能体详情转为对话端 profile 结构。 */

import type { ApplicationDetail } from '@/api/types'
import type { ConversationAppInfo } from '../../core/types'

/**
 * 只读日志只回放历史记录：不显示开场白、不发送消息，也不受显示设置影响。
 * 只保留智能体基础信息，访问与展示配置按日志场景固定：显示知识来源与执行详情，不显示头像，没有分享。
 */
export function toLogAppInfo(detail: ApplicationDetail): ConversationAppInfo {
  return {
    id: detail.id,
    name: detail.name,
    icon: detail.icon ?? '',
    desc: detail.desc,
    type: detail.type,
    prologue: detail.prologue,
    show_source: true,
    show_exec: true,
    show_share: false,
    show_avatar: false,
    show_user_avatar: false,
  }
}
