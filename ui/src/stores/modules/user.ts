import { defineStore } from 'pinia'
import type { User } from '@/api/type/user'
import UserApi from '@/api/user'

export interface userStateTypes {
  userType: number // 1 系统操作者 2 对话用户
  userInfo: User | null
  token: any
  version?: string
  accessToken?: string
  isXPack: false
}

const useUserStore = defineStore({
  id: 'user',
  state: (): userStateTypes => ({
    userType: 1,
    userInfo: null,
    token: '',
    version: '',
    isXPack: false
  }),
  actions: {
    isEnterprise() {
      return this.userInfo?.IS_XPACK && this.userInfo?.XPACK_LICENSE_IS_VALID
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
        return this.userInfo?.permissions
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

    async asyncGetVersion() {
      return UserApi.getVersion().then((ok) => {
        this.version = ok.data?.version || '-'
      })
    },

    async profile() {
      return UserApi.profile().then((ok) => {
        this.userInfo = ok.data
        this.asyncGetVersion()
      })
    },

    async login(username: string, password: string) {
      return UserApi.login({ username, password }).then((ok) => {
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
    }
  }
})

export default useUserStore
