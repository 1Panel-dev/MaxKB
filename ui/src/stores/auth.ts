/** 管理 Admin 登录凭证。 */

import { defineStore } from 'pinia'

const TOKEN_STORAGE_KEY = 'token'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: localStorage.getItem(TOKEN_STORAGE_KEY) ?? '',
  }),

  getters: {
    isAuthenticated: (state) => Boolean(state.token),
  },

  actions: {
    /** 保存当前登录凭证。 */
    setToken(token: string) {
      this.token = token
      localStorage.setItem(TOKEN_STORAGE_KEY, token)
    },

    /** 清除当前登录凭证。 */
    clearToken() {
      this.token = ''
      localStorage.removeItem(TOKEN_STORAGE_KEY)
    },
  },
})
