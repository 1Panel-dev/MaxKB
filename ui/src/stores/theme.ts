/** 管理公开外观信息并将主题色应用到运行时样式变量。 */

import { defineStore } from 'pinia'
import BaseInfoApi from '@/api/admin/auth/base-info'
import type { ThemeInfo } from '@/api/admin/auth/types'
import { DEFAULT_THEME_COLOR } from '@/constants'

function normalizeThemeColor(themeColor?: string) {
  const normalizedColor = themeColor?.trim().toLowerCase()
  return normalizedColor && /^#[\da-f]{6}$/.test(normalizedColor) ? normalizedColor : DEFAULT_THEME_COLOR
}

function getRgbChannels(themeColor: string) {
  const normalizedColor = themeColor.slice(1)
  return [0, 2, 4].map((index) => Number.parseInt(normalizedColor.slice(index, index + 2), 16)).join(' ')
}

interface ThemeState {
  themeInfo: ThemeInfo | null
}

export const useThemeStore = defineStore('theme', {
  state: (): ThemeState => ({ themeInfo: null }),
  getters: {
    isDefaultTheme: (state) => !state.themeInfo?.theme || state.themeInfo.theme === DEFAULT_THEME_COLOR, // 是默认主题
  },

  actions: {
    /** 加载、保存并应用服务端外观主题。 */
    loadThemeInfo() {
      return BaseInfoApi.getThemeInfo().then((themeInfo) => {
        return this.setTheme(themeInfo)
      })
    },

    /** 恢复并应用社区版或请求失败时使用的默认主题。 */
    resetTheme() {
      return this.setTheme({ theme: DEFAULT_THEME_COLOR })
    },

    /** 保存主题信息并同步项目运行时颜色变量。 */
    setTheme(themeInfo: ThemeInfo) {
      const themeColor = normalizeThemeColor(themeInfo.theme)
      const isDefaultTheme = themeColor === DEFAULT_THEME_COLOR
      const appliedThemeInfo = { ...themeInfo, theme: themeColor }
      const rootStyle = document.documentElement.style

      this.themeInfo = appliedThemeInfo
      rootStyle.setProperty('--mk-primary', themeColor)
      rootStyle.setProperty('--mk-primary-rgb', getRgbChannels(themeColor))
      if (isDefaultTheme) {
        rootStyle.removeProperty('--mk-primary-gradient')
        rootStyle.removeProperty('--mk-primary-gradient-end')
      } else {
        rootStyle.setProperty('--mk-primary-gradient', themeColor)
        rootStyle.setProperty('--mk-primary-gradient-end', themeColor)
      }

      return appliedThemeInfo
    },
  },
})
