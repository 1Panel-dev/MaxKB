import { defineStore } from 'pinia'
import type { User } from '@/api/type/user'
import UserApi from '@/api/user'

export interface userStateTypes {
  userType: number // 1 系统操作者 2 对话用户
  userInfo: User | null
  token: any
  version?: string
  accessToken?: string
  XPACK_LICENSE_IS_VALID: false
  isXPack: false
}

const useUserStore = defineStore({
  id: 'user',
  state: (): userStateTypes => ({
    userType: 1,
    userInfo: null,
    token: '',
    version: '',
    XPACK_LICENSE_IS_VALID: false,
    isXPack: false
  }),
  actions: {
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
          .then((ok) => {
            this.version = ok.data?.version || '-'
            this.isXPack = ok.data?.IS_XPACK
            this.XPACK_LICENSE_IS_VALID = ok.data?.XPACK_LICENSE_IS_VALID
            resolve(ok)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },

    async profile() {
      return UserApi.profile().then((ok) => {
        this.userInfo = ok.data
        this.asyncGetProfile()
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
