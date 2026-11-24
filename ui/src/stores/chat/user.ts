/** 管理当前对话用户档案与语言。 */

import { defineStore } from 'pinia'
import type { ChatUserProfile } from '@/api/types'
import ChatUserApi from '@/api/chat/chat-user'
import { normalizeLocale } from '@/locales/config'

interface ChatUserState {
  language: string
  /** 当前认证场景的语言缓存 key；门户与各单应用分别保存，不与 Admin 共用。 */
  languageStorageKey: string
  chatUserProfile: ChatUserProfile | null
}

export const useChatUserStore = defineStore('chat-user', {
  state: (): ChatUserState => ({ language: normalizeLocale(navigator.language), languageStorageKey: '', chatUserProfile: null }),

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

    /** 切换到指定场景的语言：优先使用认证前置配置的语言，其次为该场景的本地缓存，最终使用浏览器语言。 */
    applyScopeLanguage(languageStorageKey: string, profileLanguage?: string | null) {
      if (this.languageStorageKey === languageStorageKey) return
      this.languageStorageKey = languageStorageKey
      this.setLanguage(profileLanguage || localStorage.getItem(languageStorageKey) || navigator.language)
    },

    /** 更新当前语言，并持久化到当前场景的缓存。 */
    setLanguage(language: string) {
      this.language = normalizeLocale(language)
      if (this.chatUserProfile) this.chatUserProfile.language = this.language
      if (this.languageStorageKey) localStorage.setItem(this.languageStorageKey, this.language)
    },
  },
})
