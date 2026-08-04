/** 管理 Admin 登录凭证。 */

import { defineStore } from 'pinia'
import externalLoginApi from '@/api/admin/auth/external-login'
import loginApi from '@/api/admin/auth/login'
import type { LoginRequest } from '@/api/admin/auth/types'
import { useUserStore } from './user'

const TOKEN_STORAGE_KEY = 'token'

interface LoginState {
  token: string
}

export const useLoginStore = defineStore('login', {
  state: (): LoginState => ({
    token: localStorage.getItem(TOKEN_STORAGE_KEY) ?? '',
  }),

  getters: {
    isAuthenticated: (state) => Boolean(state.token),
  },

  actions: {
    async asyncLogin(loginRequest: LoginRequest) {
      const response = await loginApi.postLogin(loginRequest)
      this.setToken(response.token)
    },

    async asyncLdapLogin(loginRequest: LoginRequest) {
      const response = await loginApi.postLdapLogin(loginRequest)
      this.setToken(response.token)
    },

    async asyncLoginWithDingTalk(code: string, fromClient = false) {
      const response = fromClient
        ? await externalLoginApi.getDingTalkOauthCallback(code)
        : await externalLoginApi.getDingTalkCallback(code)
      this.setToken(response.token)
    },

    async asyncLoginWithLark(code: string) {
      const response = await externalLoginApi.getLarkOauthCallback(code)
      this.setToken(response.token)
    },

    /** 保存当前登录凭证。 */
    setToken(token: string) {
      if (token !== this.token) useUserStore().clearCurrentUser()
      this.token = token
      localStorage.setItem(TOKEN_STORAGE_KEY, token)
    },

    /** 清除当前登录凭证。 */
    clearToken() {
      this.token = ''
      localStorage.removeItem(TOKEN_STORAGE_KEY)
      useUserStore().clearCurrentUser()
    },
  },
})
