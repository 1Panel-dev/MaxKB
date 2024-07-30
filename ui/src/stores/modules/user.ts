import { defineStore } from 'pinia'
import { type Ref } from 'vue'
import type { User } from '@/api/type/user'

import UserApi from '@/api/user'
import ThemeApi from '@/api/theme'
import { useElementPlusTheme } from 'use-element-plus-theme'

export interface userStateTypes {
  userType: number // 1 系统操作者 2 对话用户
  userInfo: User | null
  token: any
  version?: string
  accessToken?: string
  XPACK_LICENSE_IS_VALID: false
  isXPack: false
  themeInfo: any
}

const useUserStore = defineStore({
  id: 'user',
  state: (): userStateTypes => ({
    userType: 1,
    userInfo: null,
    token: '',
    version: '',
    XPACK_LICENSE_IS_VALID: false,
    isXPack: false,
    themeInfo: null
  }),
  actions: {
    showXpack() {
      return this.isXPack
    },
    isDefaultTheme() {
      return !this.themeInfo?.theme || this.themeInfo?.theme === '#3370FF'
    },
    setTheme(data: any) {
      const { changeTheme } = useElementPlusTheme(this.themeInfo?.theme)
      changeTheme(data?.['theme'])
      this.themeInfo = data
    },
    isExpire() {
      return this.isXPack && !this.XPACK_LICENSE_IS_VALID
    },
    isEnterprise() {
      return this.isXPack && this.XPACK_LICENSE_IS_VALID
    },
    getToken(): String | null {
      if (this.token) {
        return this.token
      }
      return this.userType === 1 ? localStorage.getItem('token') : this.getAccessToken()
    },
    getAccessToken() {
      const accessToken = sessionStorage.getItem('accessToken')
      if (accessToken) {
        return accessToken
      }
      return localStorage.getItem('accessToken')
    },

    getPermissions() {
      if (this.userInfo) {
        return this.isXPack && this.XPACK_LICENSE_IS_VALID
          ? [...this.userInfo?.permissions, 'x-pack']
          : this.userInfo?.permissions
      } else {
        return []
      }
    },
    getRole() {
      if (this.userInfo) {
        return this.userInfo?.role
      } else {
        return ''
      }
    },
    changeUserType(num: number) {
      this.userType = num
    },

    async asyncGetProfile() {
      return new Promise((resolve, reject) => {
        UserApi.getProfile()
          .then(async (ok) => {
            this.version = ok.data?.version || '-'
            this.isXPack = ok.data?.IS_XPACK
            this.XPACK_LICENSE_IS_VALID = ok.data?.XPACK_LICENSE_IS_VALID

            if (this.isEnterprise()) {
              await this.theme()
            }
            resolve(ok)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },

    async theme(loading?: Ref<boolean>) {
      return await ThemeApi.getThemeInfo(loading).then((ok) => {
        this.setTheme(ok.data)
        window.document.title = this.themeInfo['title'] || 'MaxKB'
        // const link = document.querySelector('link[rel="icon"]') as any
        // if (link) {
        //   link['href'] = this.themeInfo['icon'] || '/favicon.ico'
        // }
      })
    },

    async profile() {
      return UserApi.profile().then(async (ok) => {
        this.userInfo = ok.data
        return this.asyncGetProfile()
      })
    },

    async login(auth_type: string, username: string, password: string) {
      return UserApi.login(auth_type, { username, password }).then((ok) => {
        this.token = ok.data
        localStorage.setItem('token', ok.data)
        return this.profile()
      })
    },

    async logout() {
      return UserApi.logout().then(() => {
        localStorage.removeItem('token')
        return true
      })
    },
    async getAuthType() {
      return UserApi.getAuthType().then((ok) => {
        return ok.data
      })
    }
  }
})

export default useUserStore
