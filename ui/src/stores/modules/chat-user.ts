import {defineStore} from 'pinia'
import ChatAPI from '@/api/chat/chat'
import type {ChatProfile, ChatUserProfile} from '@/api/type/chat'
import type {LoginRequest} from '@/api/type/user'
import type {Ref} from 'vue'
import {getBrowserLang} from '@/locales/index'

interface ChatUser {
  // 用户id
  id: string
}

interface Chat {
  chat_profile?: ChatProfile
  application?: any
  chatUserProfile?: ChatUserProfile
  token?: string
  accessToken?: string
}

const useChatUserStore = defineStore('chat-user', {
  state: (): Chat => ({
    chat_profile: undefined,
    application: undefined,
    accessToken: undefined,
  }),
  actions: {
    getLanguage() {
      return localStorage.getItem(`${this.accessToken}-locale`) || getBrowserLang()
    },
    setAccessToken(accessToken: string) {
      this.accessToken = accessToken
    },
    getChatProfile() {
      return ChatAPI.chatProfile(this.accessToken as string).then((ok) => {
        this.chat_profile = ok.data

        return this.chat_profile
      })
    },
    async getChatUserProfile() {
      const res = await ChatAPI.getChatUserProfile()
      this.chatUserProfile = res.data
      return res.data
    },
    applicationProfile() {
      return ChatAPI.applicationProfile().then((ok) => {
        console.log('applicationProfile', ok.data)
        this.application = ok.data
        localStorage.setItem(`${this.accessToken}-locale`, ok.data?.language || this.getLanguage())
      })
    },
    isAuthentication() {
      if (this.chat_profile) {
        return Promise.resolve(this.chat_profile.authentication)
      } else {
        return this.getChatProfile().then((ok) => {
          return ok.authentication
        })
      }
    },
    getToken() {
      if (this.token) {
        return this.token
      }
      const token = sessionStorage.getItem(`${this.accessToken}-accessToken`)
      if (token) {
        this.token = token
        return token
      }
      const local_token = localStorage.getItem(`${this.accessToken}-accessToken`)
      if (local_token) {
        this.token = local_token
        return local_token
      }
      return localStorage.getItem(`accessToken`)
    },
    setToken(token: string) {
      this.token = token
      sessionStorage.setItem(`${this.accessToken}-accessToken`, token)
      localStorage.setItem(`${this.accessToken}-accessToken`, token)
    },
    /**
     *匿名认证
     */
    anonymousAuthentication() {
      return ChatAPI.anonymousAuthentication(this.accessToken as string).then((ok) => {
        this.setToken(ok.data)
        return this.token
      })
    },
    passwordAuthentication(password: string) {
      return ChatAPI.passwordAuthentication(this.accessToken as string, password).then((ok) => {
        this.setToken(ok.data)
        return this.token
      })
    },
    login(request: any, loading?: Ref<boolean>) {
      return ChatAPI.login(this.accessToken as string, request, loading).then((ok) => {
        this.setToken(ok.data.token)
        return this.token
      })
    },
    ldapLogin(request: LoginRequest, loading?: Ref<boolean>) {
      return ChatAPI.ldapLogin(this.accessToken as string, request, loading).then((ok) => {
        this.setToken(ok.data.token)
        return this.token
      })
    },
    logout() {
      return ChatAPI.logout().then(() => {
        sessionStorage.removeItem(`${this.accessToken}-accessToken`)
        localStorage.removeItem(`${this.accessToken}-accessToken`)
        this.token = undefined
        return true
      })
    },
    async dingCallback(code: string, accessToken: string) {
      return ChatAPI.getDingCallback(code, accessToken).then((ok) => {
        this.setToken(ok.data.token)
        return this.token
      })
    },
    async dingOauth2Callback(code: string, accessToken: string) {
      return ChatAPI.getDingOauth2Callback(code, accessToken).then((ok) => {
        this.setToken(ok.data.token)
        return this.token
      })
    },
    async wecomCallback(code: string, accessToken: string) {
      return ChatAPI.getWecomCallback(code, accessToken).then((ok) => {
        this.setToken(ok.data.token)
        return this.token
      })
    },
    async larkCallback(code: string, accessToken: string) {
      return ChatAPI.getLarkCallback(code, accessToken).then((ok) => {
        this.setToken(ok.data.token)
        return this.token
      })
    },
    async getQrType() {
      return ChatAPI.getQrType().then((ok) => {
        return ok.data
      })
    },
    async getQrSource() {
      return ChatAPI.getQrSource().then((ok) => {
        return ok.data
      })
    },
  },
})

export default useChatUserStore
