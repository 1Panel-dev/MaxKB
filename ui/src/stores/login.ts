/** 管理 Admin 登录凭证。 */

import { defineStore } from 'pinia'
import externalLoginApi from '@/api/admin/auth/external-login'
import loginApi from '@/api/admin/auth/login'
import type { LoginRequest } from '@/types'
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
      return loginApi.postLogin(loginRequest).then((response) => this.setToken(response.token))
    },

    asyncLdapLogin(loginRequest: LoginRequest) {
      return loginApi.postLdapLogin(loginRequest).then((response) => this.setToken(response.token))
    },

    asyncLoginWithDingTalk(code: string, fromClient = false) {
      const loginRequest = fromClient
        ? externalLoginApi.getDingTalkOauthCallback(code)
        : externalLoginApi.getDingTalkCallback(code)
      return loginRequest.then((response) => this.setToken(response.token))
    },

    asyncLoginWithLark(code: string) {
      return externalLoginApi
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
