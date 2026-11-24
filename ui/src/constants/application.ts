/** 智能体共享常量。 */

import { computed, reactive } from 'vue'
import type { ApplicationDisplaySetting } from '@/api/types'
import { t } from '@/locales'

/** 显示设置默认值：专业版显示设置弹窗的初始与恢复默认，社区版调试面板也以此展示。使用方按需深拷贝。 */
export const APPLICATION_DISPLAY_SETTING_DEFAULT: Readonly<ApplicationDisplaySetting> = reactive({
  show_source: false,
  show_exec: false,
  show_history: true,
  draggable: true,
  show_share: true,
  icon: '',
  chat_background: '',
  avatar: './favicon.ico',
  float_icon: '',
  user_avatar: './favicon.ico',
  disclaimer: false,
  disclaimer_value: computed(() => t('application.overview.display.defaultDisclaimer')),
  custom_theme: { theme_color: '', header_font_color: '#1f2329' },
  float_location: { x: { type: 'right', value: 0 }, y: { type: 'bottom', value: 30 } },
  show_avatar: false,
  show_user_avatar: false,
})
