import { defineStore } from 'pinia'
import { type Ref } from 'vue'
import type { User } from '@/api/type/user'
import UserApi from '@/api/user/user'
import LoginApi from '@/api/user/login'
import { cloneDeep } from 'lodash'
import ThemeApi from '@/api/system-settings/theme'
import { useLocalStorage } from '@vueuse/core'
// import { defaultPlatformSetting } from '@/utils/theme'

import { localeConfigKey, getBrowserLang } from '@/locales/index'
import useThemeStore from './theme'
import { useElementPlusTheme } from 'use-element-plus-theme'
import { defaultPlatformSetting } from '@/utils/theme.ts'
import useLoginStore from './login'

export interface userStateTypes {
  userType: number // 1 系统操作者 2 对话用户
  userInfo: User | null
  version?: string
  license_is_valid: boolean
  edition: 'CE' | 'PE' | 'EE'
  themeInfo: any
  workspace_id: string
}

const useUserStore = defineStore('user', {
  state: (): userStateTypes => ({
    userType: 1, // 1 系统操作者 2 对话用户
    userInfo: null,
    version: '',
    license_is_valid: false,
    edition: 'CE',
    themeInfo: null,
    workspace_id: '',
  }),
  actions: {
    getLanguage() {
      return this.userType === 1
        ? localStorage.getItem('MaxKB-locale') || getBrowserLang()
        : sessionStorage.getItem('language') || getBrowserLang()
    },
    isDefaultTheme() {
      return !this.themeInfo?.theme || this.themeInfo?.theme === '#3370FF'
    },
    setTheme(data: any) {
      const { changeTheme } = useElementPlusTheme(this.themeInfo?.theme)
      changeTheme(data?.['theme'])
      this.themeInfo = cloneDeep(data)
    },
    setWorkspaceId(workspace_id: string) {
      this.workspace_id = workspace_id
      localStorage.setItem('workspace_id', workspace_id)
    },
    getWorkspaceId(): string | null {
      this.workspace_id = this.workspace_id || localStorage.getItem('workspace_id') || 'default'
      return this.workspace_id
    },

    getPermissions() {
      if (this.userInfo) {
        if (this.isEE()) {
          return [...this.userInfo?.permissions, 'X-PACK-EE']
        } else if (this.isPE()) {
          return [...this.userInfo?.permissions, 'X-PACK-PE']
        }
        return this.userInfo?.permissions
      } else {
        return []
      }
    },
    getEdition() {
      if (this.userInfo) {
        if (this.isEE()) {
          return 'X-PACK-EE'
        } else if (this.isPE()) {
          return 'X-PACK-PE'
        } else {
          return 'X-PACK-CE'
        }
      }
      return 'X-PACK-CE'
    },
    getRole() {
      if (this.userInfo) {
        return this.userInfo?.role
      } else {
        return []
      }
    },

    showXpack() {
      return this.edition != 'CE'
    },
    isEnterprise() {
      return this.edition != 'CE' && !this.license_is_valid
    },
    isExpire() {
      return this.edition != 'CE' && !this.license_is_valid
    },
    isCE() {
      return this.edition == 'CE' && this.license_is_valid
    },
    isPE() {
      return this.edition == 'PE' && this.license_is_valid
    },
    isEE() {
      return this.edition == 'EE' && this.license_is_valid
    },
    changeUserType(num: number, token?: string) {
      this.userType = num
      const login = useLoginStore()
      login.userAccessToken = token || ''
    },
    async theme(loading?: Ref<boolean>) {
      return await ThemeApi.getThemeInfo(loading).then((ok) => {
        this.setTheme(ok.data)
        // window.document.title = this.themeInfo['title'] || 'MaxKB'
        // const link = document.querySelector('link[rel="icon"]') as any
        // if (link) {
        //   link['href'] = this.themeInfo['icon'] || '/favicon.ico'
        // }
      })
    },
    async profile(loading?: Ref<boolean>) {
      return UserApi.getUserProfile(loading).then((ok) => {
        this.userInfo = ok.data
        useLocalStorage<string>(localeConfigKey, 'en-US').value =
          ok?.data?.language || this.getLanguage()
        const theme = useThemeStore()
        theme.setTheme()
        return this.asyncGetProfile()
      })
    },

    async asyncGetProfile() {
      return new Promise((resolve, reject) => {
        UserApi.getProfile()
          .then(async (ok) => {
            // this.version = ok.data?.version || '-'
            this.license_is_valid = ok.data.license_is_valid
            this.edition = ok.data.edition

            if (this.isEE() || this.isPE()) {
              await this.theme()
            } else {
              this.themeInfo = {
                ...defaultPlatformSetting,
              }
            }
            resolve(ok)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },
    async postUserLanguage(lang: string, loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        LoginApi.postLanguage({ language: lang }, loading)
          .then(async (ok) => {
            useLocalStorage(localeConfigKey, 'en-US').value = lang
            window.location.reload()
            resolve(ok)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },
  },
})

export default useUserStore
