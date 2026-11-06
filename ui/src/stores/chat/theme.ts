/** 管理 Chat 入口的智能体主题色，并按需应用到当前文档。 */

import { defineStore } from 'pinia'
import { DEFAULT_THEME_COLOR } from '@/constants'

export const useChatThemeStore = defineStore('chat-theme', {
  state: () => ({ themeColor: DEFAULT_THEME_COLOR }),

  actions: {
    /** 配置缺失或非法时使用默认色；主题只保存在内存中。 */
    setTheme(themeColor?: string) {
      const normalizedColor = themeColor?.trim().toLowerCase()
      this.themeColor = normalizedColor && /^#[\da-f]{6}$/.test(normalizedColor) ? normalizedColor : DEFAULT_THEME_COLOR

      const rootStyle = document.documentElement.style
      const hexColor = this.themeColor.slice(1)
      const rgbChannels = [0, 2, 4].map((index) => Number.parseInt(hexColor.slice(index, index + 2), 16)).join(' ')
      rootStyle.setProperty('--mk-primary', this.themeColor)
      rootStyle.setProperty('--mk-primary-rgb', rgbChannels)
      if (this.themeColor === DEFAULT_THEME_COLOR) {
        rootStyle.removeProperty('--mk-primary-gradient')
        rootStyle.removeProperty('--mk-primary-gradient-end')
      } else {
        rootStyle.setProperty('--mk-primary-gradient', this.themeColor)
        rootStyle.setProperty('--mk-primary-gradient-end', this.themeColor)
      }
    },

    /** 恢复默认主题色与默认蓝紫渐变。 */
    resetTheme() {
      this.setTheme()
    },
  },
})
