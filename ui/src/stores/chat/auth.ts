/**
 * 管理对话端的认证前置配置与当前 token。
 *
 * 门户与各单应用是不同的认证场景（scope）：门户为 `PORTAL_AUTH_SCOPE`，单应用为其 accessToken。
 * Store 只保存当前场景的一份 token，各场景的 token 在本地存储中分别保存。
 */

import { defineStore } from 'pinia'
import ChatAuthApi from '@/api/chat/auth'
import type { ApplicationAuthProfileMeta, AuthProfile, ChatLoginRequest } from '@/api/types'
import { useChatUserStore } from './user'

/** 门户的认证场景；accessToken 为 16 位十六进制字符串，不会与之重名。 */
export const PORTAL_AUTH_SCOPE = 'portal'

function isPortalScope(scope: string) {
  return scope === PORTAL_AUTH_SCOPE
}

/** 门户场景不向接口传 accessToken。 */
function getAccessToken(scope: string) {
  return isPortalScope(scope) ? undefined : scope
}

function getTokenStorageKey(scope: string) {
  return isPortalScope(scope) ? 'chat-portal-token' : `chat-application-token-${scope}`
}

/** 读取本地保存的 token，包括已失效的；匿名认证与登录时携带，后端据此沿用同一对话用户。 */
function getSavedToken(scope: string) {
  return localStorage.getItem(getTokenStorageKey(scope)) || undefined
}

interface ChatAuthState {
  /** 当前认证场景，只在守卫放行前切换。 */
  scope: string
  token: string
  /** 本次页面中已失效（401）的 token；仍保留在本地存储中，供重新认证时携带。 */
  expiredToken: string
  authProfile: AuthProfile<unknown> | null
}

export const useChatAuthStore = defineStore('chat-auth', {
  state: (): ChatAuthState => ({ scope: '', token: '', expiredToken: '', authProfile: null }),

  getters: {
    isAuthenticated: (state) => Boolean(state.token),
    isPortal: (state) => isPortalScope(state.scope),
    /** 当前单应用的 accessToken；门户场景为 undefined。 */
    accessToken: (state) => getAccessToken(state.scope),
    /** 当前单应用的智能体 ID；门户场景为 undefined，由路由参数提供。 */
    applicationId(state): string | undefined {
      if (isPortalScope(state.scope)) return undefined
      return (state.authProfile?.meta as ApplicationAuthProfileMeta | undefined)?.application_id
    },
  },

  actions: {
    /** 读取指定场景已保存的有效 token，不改变当前场景；已失效的 token 视为没有。 */
    getStoredToken(scope: string) {
      const token = getSavedToken(scope) ?? ''
      return token === this.expiredToken ? '' : token
    },

    /** 获取指定场景的认证前置配置；与当前场景相同时复用。 */
    fetchAuthProfile(scope: string): Promise<AuthProfile<unknown>> {
      if (scope === this.scope && this.authProfile) return Promise.resolve(this.authProfile)

      return isPortalScope(scope) ? ChatAuthApi.getPortalAuthProfile() : ChatAuthApi.getApplicationAuthProfile(scope)
    },

    /** 切换当前场景，由守卫在放行前调用。 */
    activate(scope: string, authProfile: AuthProfile<unknown>) {
      if (scope !== this.scope) useChatUserStore().clearCurrentUser()
      this.scope = scope
      this.authProfile = authProfile
      this.token = this.getStoredToken(scope)
    },

    /** 获取并保存指定场景的匿名访问 token，携带本地保存的 token 以沿用同一对话用户。 */
    postAnonymousAuth(scope: string) {
      return ChatAuthApi.postAnonymousAuth(getAccessToken(scope), getSavedToken(scope)).then((token) => {
        this.setToken(token, scope)
        return token
      })
    },

    /** 使用账号登录当前场景，携带本地保存的 token。 */
    login(loginRequest: ChatLoginRequest) {
      return ChatAuthApi.postLogin(loginRequest, getAccessToken(this.scope), getSavedToken(this.scope)).then(({ token }) => {
        this.setToken(token, this.scope)
        return token
      })
    },

    /** 退出当前场景的登录状态。 */
    logout() {
      return ChatAuthApi.postLogout().then(() => this.clearToken())
    },

    /** 保存指定场景的 token；是当前场景时同步到 Store。 */
    setToken(token: string, scope: string) {
      localStorage.setItem(getTokenStorageKey(scope), token)
      if (scope !== this.scope) return

      if (token !== this.token) useChatUserStore().clearCurrentUser()
      this.token = token
    },

    /** 当前 token 失效（401）：Store 中清除，本地存储保留，重新认证时携带。 */
    expireToken() {
      this.expiredToken = getSavedToken(this.scope) ?? ''
      this.token = ''
      useChatUserStore().clearCurrentUser()
    },

    /** 清除当前场景的 token，如退出登录。 */
    clearToken() {
      localStorage.removeItem(getTokenStorageKey(this.scope))
      this.token = ''
      useChatUserStore().clearCurrentUser()
    },
  },
})
