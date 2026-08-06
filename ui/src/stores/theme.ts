/** 管理公开外观信息并将主题色应用到运行时样式变量。 */

import { defineStore } from 'pinia'
import BaseInfoApi from '@/api/admin/auth/base-info'
import type { ThemeInfo } from '@/api/admin/auth/types'

const DEFAULT_THEME_COLOR = '#3370ff'
const DEFAULT_THEME_INFO: ThemeInfo = {
  showForum: true,
  showProject: true,
  showUserManual: true,
  theme: DEFAULT_THEME_COLOR,
  title: 'MaxKB',
}

function getRgbChannels(hexColor: string) {
  const normalizedColor = hexColor.replace('#', '')
  if (!/^[\da-f]{6}$/i.test(normalizedColor)) return null
  return [0, 2, 4]
    .map((index) => Number.parseInt(normalizedColor.slice(index, index + 2), 16))
    .join(' ')
}

interface ThemeState {
  themeInfo: ThemeInfo
}

export const useThemeStore = defineStore('theme', {
  state: (): ThemeState => ({
    themeInfo: { ...DEFAULT_THEME_INFO },
  }),

  actions: {
    /** 加载、保存并应用服务端外观主题。 */
    loadThemeInfo() {
      return BaseInfoApi.getThemeInfo().then((themeInfo) => {
        this.applyThemeInfo(themeInfo)
        return this.themeInfo
      })
    },

    /** 恢复并应用社区版或请求失败时使用的默认主题。 */
    applyDefaultTheme() {
      this.applyThemeInfo(DEFAULT_THEME_INFO)
    },

    /** 保存主题信息并同步项目运行时颜色变量。 */
    applyThemeInfo(themeInfo: ThemeInfo) {
      this.themeInfo = { ...DEFAULT_THEME_INFO, ...themeInfo }
      const themeColor = this.themeInfo.theme || DEFAULT_THEME_COLOR
      const rootStyle = document.documentElement.style
      rootStyle.setProperty('--mk-primary', themeColor)
      const rgbChannels = getRgbChannels(themeColor)
      if (rgbChannels) rootStyle.setProperty('--mk-primary-rgb', rgbChannels)
    },
  },
})
