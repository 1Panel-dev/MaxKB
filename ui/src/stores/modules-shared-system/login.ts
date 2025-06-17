import {defineStore} from 'pinia'
import {type Ref} from 'vue'
import loginApi from '@/api/user/login'
import type { LoginRequest } from '@/api/type/login'

import useUserStore from '@/stores/modules/user'

const useLoginStore = defineStore('logi', {
  state: () => ({
    token: '',
    userAccessToken: '',
  }),
  actions: {
    getToken(): string | null {
      if (this.token) {
        return this.token
      }
      const user = useUserStore()
      return user.userType === 1 ? localStorage.getItem('token') : this.getAccessToken()
    },
    getAccessToken() {
      const token = sessionStorage.getItem(`${this.userAccessToken}-accessToken`)
      if (token) {
        return token
      }
      const local_token = localStorage.getItem(`${token}-accessToken`)
      if (local_token) {
        return local_token
      }
      return localStorage.getItem(`accessToken`)
    },

    async asyncLogin(data: LoginRequest, loading?: Ref<boolean>) {
      return loginApi.login(data).then((ok) => {
        this.token = ok?.data?.token
        localStorage.setItem('token', ok?.data?.token)
        const user = useUserStore()
        return user.profile(loading)
      })
    },
    async asyncLdapLogin(data: LoginRequest, loading?: Ref<boolean>) {
      return loginApi.ldapLogin(data).then((ok) => {
        this.token = ok?.data?.token
        localStorage.setItem('token', ok?.data?.token)
        const user = useUserStore()
        return user.profile(loading)
      })
    },
  },
})

export default useLoginStore
