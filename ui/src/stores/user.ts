/** 管理 Admin 用户相关的共享状态。 */

import { defineStore } from 'pinia'

const LANGUAGE_STORAGE_KEY = 'MaxKB-locale'

function getDefaultLanguage() {
  return localStorage.getItem(LANGUAGE_STORAGE_KEY) || navigator.language || 'en-US'
}

export const useUserStore = defineStore('user', {
  state: () => ({
    language: getDefaultLanguage(),
  }),

  actions: {
    /** 更新并持久化当前用户语言。 */
    setLanguage(language: string) {
      this.language = language
      localStorage.setItem(LANGUAGE_STORAGE_KEY, language)
    },
  },
})
