/** 管理 Admin 用户相关的共享状态。 */

import { defineStore } from 'pinia'
import currentUserApi from '@/api/admin/auth/current-user'
import type { CurrentUser, WorkspaceSummary } from '@/api/admin/auth/types'

const LANGUAGE_STORAGE_KEY = 'MaxKB-locale'
const WORKSPACE_STORAGE_KEY = 'workspace_id'
const DEFAULT_WORKSPACE: WorkspaceSummary = { id: 'default', name: 'default' }

function getDefaultLanguage() {
  return localStorage.getItem(LANGUAGE_STORAGE_KEY) || navigator.language || 'en-US'
}

interface UserState {
  language: string
  userInfo: CurrentUser | null
  workspaceId: string
  workspaceList: WorkspaceSummary[]
}

export const useUserStore = defineStore('user', {
  state: (): UserState => ({
    language: getDefaultLanguage(),
    userInfo: null,
    workspaceId: localStorage.getItem(WORKSPACE_STORAGE_KEY) ?? '',
    workspaceList: [],
  }),

  getters: {
    is_admin: (state) => state.userInfo?.role.includes('ADMIN') ?? false,
  },

  actions: {
    /** 加载当前用户，并校验语言和当前工作空间。 */
    async loadCurrentUser() {
      this.userInfo = await currentUserApi.getCurrentUser()
      if (this.userInfo.language) this.setLanguage(this.userInfo.language)
      this.workspaceList = this.userInfo.workspace_list?.length
        ? this.userInfo.workspace_list
        : [{ ...DEFAULT_WORKSPACE }]
      const workspaceExists = this.workspaceList.some(
        (workspace) => workspace.id === this.workspaceId,
      )
      if (!workspaceExists) this.setWorkspaceId(this.workspaceList[0]?.id ?? DEFAULT_WORKSPACE.id)
      return this.userInfo
    },

    /** 清除仅在登录状态下有效的用户数据。 */
    clearCurrentUser() {
      this.userInfo = null
      this.workspaceId = ''
      this.workspaceList = []
      localStorage.removeItem(WORKSPACE_STORAGE_KEY)
    },

    /** 更新并持久化当前用户语言。 */
    setLanguage(language: string) {
      this.language = language
      localStorage.setItem(LANGUAGE_STORAGE_KEY, language)
    },

    /** 更新并持久化当前工作空间。 */
    setWorkspaceId(workspaceId: string) {
      this.workspaceId = workspaceId
      localStorage.setItem(WORKSPACE_STORAGE_KEY, workspaceId)
    },
  },
})
