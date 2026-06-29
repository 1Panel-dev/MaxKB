import { defineStore } from 'pinia'
import { cloneDeep } from 'lodash'
import { useElementPlusTheme } from 'use-element-plus-theme'
import ThemeApi from '@/api/system-settings/theme'
import {
  getDarkMode,
  setDarkMode as setDarkModeUtil,
  applyDarkMode,
  initDarkMode,
  type DarkModeType,
} from '@/utils/theme'
import type { Ref } from 'vue'

export interface themeStateTypes {
  themeInfo: any
  darkMode: DarkModeType
}

const defaultColor = '#1A6DFF'

const useThemeStore = defineStore('theme', {
  state: (): themeStateTypes => ({
    themeInfo: null,
    darkMode: getDarkMode(),
  }),
  getters: {
    isDarkMode(): boolean {
      const root = document.documentElement
      return root.getAttribute('data-theme') === 'dark'
    },
  },
  actions: {
    isDefaultTheme() {
      return !this.themeInfo?.theme || this.themeInfo?.theme === defaultColor
    },

    setTheme(data?: any) {
      const { changeTheme } = useElementPlusTheme(this.themeInfo?.theme || defaultColor)
      changeTheme(data?.['theme'] || defaultColor)
      this.themeInfo = cloneDeep(data)
    },

    setDarkMode(mode: DarkModeType) {
      this.darkMode = mode
      setDarkModeUtil(mode)
    },

    async theme(loading?: Ref<boolean>) {
      return await ThemeApi.getThemeInfo(loading).then((ok) => {
        this.setTheme(ok.data)
        // Apply dark mode on init
        initDarkMode()
      })
    },
  },
})

export default useThemeStore
