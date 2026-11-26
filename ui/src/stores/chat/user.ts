/** 管理当前对话用户档案与语言。 */

import { defineStore } from 'pinia'
import type { ChatUserProfile } from '@/api/types'
import ChatUserApi from '@/api/chat/chat-user'
import { normalizeLocale } from '@/locales/config'

interface ChatUserState {
  language: string
  chatUserProfile: ChatUserProfile | null
}

export const useChatUserStore = defineStore('chat-user', {
  state: (): ChatUserState => ({ language: normalizeLocale(navigator.language), chatUserProfile: null }),

  actions: {
    /** 加载当前对话用户档案，并应用账号语言。 */
    loadCurrentUser() {
      return ChatUserApi.getChatUserProfile().then((chatUserProfile) => {
        this.chatUserProfile = chatUserProfile
        if (chatUserProfile.language) this.setLanguage(chatUserProfile.language)
        return chatUserProfile
      })
    },

    /** 清除仅在当前 token 下有效的用户档案。 */
    clearCurrentUser() {
      this.chatUserProfile = null
    },

    /** 更新当前语言与用户档案，不使用浏览器缓存。 */
    setLanguage(language: string) {
      this.language = normalizeLocale(language)
      if (this.chatUserProfile) this.chatUserProfile.language = this.language
    },
  },
})
