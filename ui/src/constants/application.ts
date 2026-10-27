/** 智能体共享常量。 */

import type { ApplicationDisplaySetting } from '@/api/types'

/** 显示设置默认值：专业版显示设置弹窗的初始与恢复默认，社区版调试面板也以此展示。使用方按需深拷贝。 */
export const APPLICATION_DISPLAY_SETTING_DEFAULT: Readonly<ApplicationDisplaySetting> = {
  show_source: false,
  show_exec: false,
  language: '',
  show_history: true,
  draggable: true,
  show_share: true,
  icon: '',
  chat_background: '',
  avatar: './favicon.ico',
  float_icon: '',
  user_avatar: './favicon.ico',
  disclaimer: false,
  disclaimer_value: '「以上内容均由 AI 生成，仅供参考和借鉴」',
  custom_theme: { theme_color: '', header_font_color: '#1f2329' },
  float_location: { x: { type: 'right', value: 0 }, y: { type: 'bottom', value: 30 } },
  show_avatar: true,
  show_user_avatar: true,
}
