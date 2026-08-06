/** 管理 Admin 登录凭证。 */

import { defineStore } from 'pinia'
import ExternalLoginApi from '@/api/admin/auth/external-login'
import LoginApi from '@/api/admin/auth/login'
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
    asyncLogin(loginRequest: LoginRequest) {
      return LoginApi.postLogin(loginRequest).then((response) => this.setToken(response.token))
    },

    asyncLdapLogin(loginRequest: LoginRequest) {
      return LoginApi.postLdapLogin(loginRequest).then((response) => this.setToken(response.token))
    },

    asyncLoginWithDingTalk(code: string, fromClient = false) {
      const loginRequest = fromClient
        ? ExternalLoginApi.getDingTalkOauthCallback(code)
        : ExternalLoginApi.getDingTalkCallback(code)
      return loginRequest.then((response) => this.setToken(response.token))
    },

    asyncLoginWithLark(code: string) {
      return ExternalLoginApi
        .getLarkOauthCallback(code)
        .then((response) => this.setToken(response.token))
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
