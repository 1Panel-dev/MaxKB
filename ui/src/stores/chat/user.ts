/** 管理当前对话用户档案与语言。 */

import { defineStore } from 'pinia'
import ChatUserApi from '@/api/chat/chat-user'
import type { ChatUserProfile } from '@/api/types'

const LANGUAGE_STORAGE_KEY = 'MaxKB-locale'

function getDefaultLanguage() {
  return localStorage.getItem(LANGUAGE_STORAGE_KEY) || navigator.language || 'en-US'
}

interface ChatUserState {
  language: string
  chatUserProfile: ChatUserProfile | null
}

export const useChatUserStore = defineStore('chat-user', {
  state: (): ChatUserState => ({ language: getDefaultLanguage(), chatUserProfile: null }),

  actions: {
    /** 加载当前对话用户档案。 */
    loadCurrentUser() {
      return ChatUserApi.getChatUserProfile().then((chatUserProfile) => {
        this.chatUserProfile = chatUserProfile
        return chatUserProfile
      })
    },

    /** 清除仅在当前 token 下有效的用户档案。 */
    clearCurrentUser() {
      this.chatUserProfile = null
    },

    /** 更新并持久化当前语言。 */
    setLanguage(language: string) {
      this.language = language
      localStorage.setItem(LANGUAGE_STORAGE_KEY, language)
    },
  },
})
