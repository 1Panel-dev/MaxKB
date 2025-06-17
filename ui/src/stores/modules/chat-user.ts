import { defineStore } from 'pinia'
import ChatAPI from '@/api/chat/chat'
import { type ChatProfile } from '@/api/type/chat'

interface ChatUser {
  // 用户id
  id: string
}
interface Application {}
interface Chat {
  chat_profile?: ChatProfile
  application?: Application
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
    setAccessToken(accessToken: string) {
      this.accessToken = accessToken
    },
    getChatProfile() {
      return ChatAPI.chatProfile(this.accessToken as string).then((ok) => {
        this.chat_profile = ok.data
        return this.chat_profile
      })
    },
    applicationProfile() {
      return ChatAPI.applicationProfile().then((ok) => {
        this.application = ok.data
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
    /**
     *匿名认证
     */
    anonymousAuthentication() {
      return ChatAPI.anonymousAuthentication(this.accessToken as string).then((ok) => {
        this.token = ok.data
        return this.token
      })
    },
  },
})

export default useChatUserStore
