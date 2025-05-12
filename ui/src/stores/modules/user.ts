import { defineStore } from 'pinia'
import { type Ref } from 'vue'
import type { User } from '@/api/type/user'
import { cloneDeep } from 'lodash'
import UserApi from '@/api/user/user'
// import ThemeApi from '@/api/theme'
// import { useElementPlusTheme } from 'use-element-plus-theme'
// import { defaultPlatformSetting } from '@/utils/theme'
import { useLocalStorage } from '@vueuse/core'
import { localeConfigKey, getBrowserLang } from '@/locales/index'
import useThemeStore from './theme'
export interface userStateTypes {
  userType: number // 1 系统操作者 2 对话用户
  userInfo: User | null
  version?: string
  XPACK_LICENSE_IS_VALID: false
  isXPack: false
}

const useLoginStore = defineStore('user', {
  state: (): userStateTypes => ({
    userType: 1, // 1 系统操作者 2 对话用户
    userInfo: null,
    version: '',
    XPACK_LICENSE_IS_VALID: false,
    isXPack: false,
  }),
  actions: {
    getLanguage() {
      return this.userType === 1
        ? localStorage.getItem('MaxKB-locale') || getBrowserLang()
        : sessionStorage.getItem('language') || getBrowserLang()
    },
    async profile(loading?: Ref<boolean>) {
      return UserApi.getUserProfile(loading).then((ok) => {
        this.userInfo = ok.data
        useLocalStorage<string>(localeConfigKey, 'en-US').value =
          ok?.data?.language || this.getLanguage()
        const theme = useThemeStore()
        theme.setTheme()
        // return this.asyncGetProfile()
      })
    },
    // async asyncGetProfile() {
    //   return new Promise((resolve, reject) => {
    //     UserApi.getProfile()
    //       .then(async (ok) => {
    //         this.version = ok.data?.version || '-'
    //         this.isXPack = ok.data?.IS_XPACK
    //         this.XPACK_LICENSE_IS_VALID = ok.data?.XPACK_LICENSE_IS_VALID

    //         if (this.isEnterprise()) {
    //           await this.theme()
    //         } else {
    //           this.themeInfo = {
    //             ...defaultPlatformSetting
    //           }
    //         }
    //         resolve(ok)
    //       })
    //       .catch((error) => {
    //         reject(error)
    //       })
    //   })
    // },

    getPermissions() {
      if (this.userInfo) {
        return this.isXPack && this.XPACK_LICENSE_IS_VALID
          ? [...this.userInfo?.permissions, 'x-pack']
          : this.userInfo?.permissions
      } else {
        return this.userInfo?.permissions
      }
    },
    getRole() {
      if (this.userInfo) {
        return this.userInfo?.role
      } else {
        return ''
      }
    },
    // showXpack() {
    //   return this.isXPack
    // },

    // isExpire() {
    //   return this.isXPack && !this.XPACK_LICENSE_IS_VALID
    // },
    // isEnterprise() {
    //   return this.isXPack && this.XPACK_LICENSE_IS_VALID
    // },

    // changeUserType(num: number, token?: string) {
    //   this.userType = num
    //   this.userAccessToken = token
    // },



    // async dingCallback(code: string) {
    //   return UserApi.getDingCallback(code).then((ok) => {
    //     this.token = ok.data
    //     localStorage.setItem('token', ok.data)
    //     return this.profile()
    //   })
    // },
    // async dingOauth2Callback(code: string) {
    //   return UserApi.getDingOauth2Callback(code).then((ok) => {
    //     this.token = ok.data
    //     localStorage.setItem('token', ok.data)
    //     return this.profile()
    //   })
    // },
    // async wecomCallback(code: string) {
    //   return UserApi.getWecomCallback(code).then((ok) => {
    //     this.token = ok.data
    //     localStorage.setItem('token', ok.data)
    //     return this.profile()
    //   })
    // },
    // async larkCallback(code: string) {
    //   return UserApi.getlarkCallback(code).then((ok) => {
    //     this.token = ok.data
    //     localStorage.setItem('token', ok.data)
    //     return this.profile()
    //   })
    // },

    // async logout() {
    //   return UserApi.logout().then(() => {
    //     localStorage.removeItem('token')
    //     return true
    //   })
    // },
    // async getAuthType() {
    //   return UserApi.getAuthType().then((ok) => {
    //     return ok.data
    //   })
    // },
    // async getQrType() {
    //   return UserApi.getQrType().then((ok) => {
    //     return ok.data
    //   })
    // },
    // async getQrSource() {
    //   return UserApi.getQrSource().then((ok) => {
    //     return ok.data
    //   })
    // },
    // async postUserLanguage(lang: string, loading?: Ref<boolean>) {
    //   return new Promise((resolve, reject) => {
    //     UserApi.postLanguage({ language: lang }, loading)
    //       .then(async (ok) => {
    //         useLocalStorage(localeConfigKey, 'en-US').value = lang
    //         window.location.reload()
    //         resolve(ok)
    //       })
    //       .catch((error) => {
    //         reject(error)
    //       })
    //   })
    // }
  },
})

export default useLoginStore
