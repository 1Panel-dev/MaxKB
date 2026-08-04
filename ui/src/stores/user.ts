/** 管理 Admin 用户相关的共享状态。 */

import { defineStore } from 'pinia'
import currentUserApi from '@/api/admin/auth/current-user'
import type { CurrentUser, WorkspaceSummary } from '@/api/admin/auth/types'

const LANGUAGE_STORAGE_KEY = 'MaxKB-locale'
const WORKSPACE_STORAGE_KEY = 'workspace_id'
const DEFAULT_WORKSPACE: WorkspaceSummary = { id: 'default', name: 'default' }

function getDefaultLanguage() {
  return localStorage.getItem(LANGUAGE_STORAGE_KEY) || navigator.language || 'en-US'
}

interface UserState {
  language: string
  userInfo: CurrentUser | null
}

export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    language: getDefaultLanguage(),
    userInfo: null,
  }),

  getters: {
    is_admin: (state) => state.userInfo?.role.includes('ADMIN') ?? false,
  },

  actions: {
    /** 加载当前用户，并校验语言和当前工作空间。 */
    loadCurrentUser() {
      return currentUserApi.getCurrentUser().then((userInfo) => {
        this.userInfo = userInfo
        if (userInfo.language) this.setLanguage(userInfo.language)

        return userInfo
      })
    },

    /** 清除仅在登录状态下有效的用户数据。 */
    clearCurrentUser() {
      this.userInfo = null
      localStorage.removeItem(WORKSPACE_STORAGE_KEY)
    },

    /** 更新并持久化当前用户语言。 */
    setLanguage(language: string) {
      this.language = language
      localStorage.setItem(LANGUAGE_STORAGE_KEY, language)
    },

  },
})
