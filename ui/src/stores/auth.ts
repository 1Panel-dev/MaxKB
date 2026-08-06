/** 管理 Admin 认证凭证及登录前可访问的平台公开档案。 */

import { defineStore } from 'pinia'
import BaseInfoApi from '@/api/admin/auth/base-info'
import ExternalLoginApi from '@/api/admin/auth/external-login'
import LoginApi from '@/api/admin/auth/login'
import type { BaseProfile, LoginRequest } from '@/api/admin/auth/types'
import { useUserStore } from './user'

const TOKEN_STORAGE_KEY = 'token'

interface AuthState {
  baseProfile: BaseProfile | null
  token: string
}

export const useAuthStore = defineStore('auth', {
  state: (): AuthState => ({
    baseProfile: null,
    token: localStorage.getItem(TOKEN_STORAGE_KEY) ?? '',
  }),

  getters: {
    isAuthenticated: (state) => Boolean(state.token),
    showXpack: (state) => Boolean(state.baseProfile && state.baseProfile.edition !== 'CE'),
    isExpire: (state) =>
      Boolean(
        state.baseProfile &&
        state.baseProfile.edition !== 'CE' &&
        !state.baseProfile.license_is_valid,
      ),
    isCE: (state) => state.baseProfile?.edition === 'CE',
    isPE: (state) => state.baseProfile?.edition === 'PE' && state.baseProfile.license_is_valid,
    isEE: (state) => state.baseProfile?.edition === 'EE' && state.baseProfile.license_is_valid,
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
      return ExternalLoginApi.getLarkOauthCallback(code).then((response) =>
        this.setToken(response.token),
      )
    },

    /** 加载并缓存登录前所需的平台公开档案。 */
    loadBaseProfile() {
      if (this.baseProfile) return Promise.resolve(this.baseProfile)

      return BaseInfoApi.getBaseProfile().then((baseProfile) => {
        this.baseProfile = baseProfile
        return baseProfile
      })
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
