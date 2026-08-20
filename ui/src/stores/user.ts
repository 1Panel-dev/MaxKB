/** 管理 Admin 用户相关的共享状态。 */

import { defineStore } from 'pinia'
import CurrentUserApi from '@/api/admin/auth/current-user'
import type { CurrentUserInfo } from '@/api/admin/auth/types'
import { ROLE_TYPE } from '@/api/enums'

const LANGUAGE_STORAGE_KEY = 'MaxKB-locale'

function getDefaultLanguage() {
  return localStorage.getItem(LANGUAGE_STORAGE_KEY) || navigator.language || 'en-US'
}

interface UserState {
  language: string
  userInfo: CurrentUserInfo | null
}

export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    language: getDefaultLanguage(),
    userInfo: null,
  }),

  getters: {
    is_admin: (state) => state.userInfo?.role.includes(ROLE_TYPE.ADMIN) ?? false,

    /** 当前用户角色集合，供权限模块（@/permission）判定使用。getter 已缓存。 */
    roleSet: (state): Set<string> => new Set(state.userInfo?.role ?? []),

    /** 当前用户权限位图（组 key → BigInt 位掩码），供权限模块判定使用。getter 已缓存。 */
    permissionMap: (state): Map<string, bigint> => {
      const source = state.userInfo?.permissions ?? {}
      const result = new Map<string, bigint>()
      for (const [key, value] of Object.entries(source)) {
        result.set(key, BigInt(value ?? 0))
      }
      return result
    },
  },

  actions: {
    /** 加载当前用户，并同步当前语言。 */
    loadCurrentUser() {
      return CurrentUserApi.getCurrentUserInfo().then((userInfo) => {
        this.userInfo = userInfo
        if (userInfo.language) this.setLanguage(userInfo.language)

        return userInfo
      })
    },

    /** 清除仅在登录状态下有效的用户数据。 */
    clearCurrentUser() {
      this.userInfo = null
    },

    /** 更新并持久化当前用户语言。 */
    setLanguage(language: string) {
      this.language = language
      localStorage.setItem(LANGUAGE_STORAGE_KEY, language)
    },
  },
})
