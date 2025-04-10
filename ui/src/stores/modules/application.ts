import { defineStore } from 'pinia'
import applicationApi from '@/api/application'
import applicationXpackApi from '@/api/application-xpack'
import { type Ref } from 'vue'
import { getBrowserLang } from '@/locales/index'
import useUserStore from './user'
const useApplicationStore = defineStore({
  id: 'application',
  state: () => ({
    location: `${window.location.origin}/ui/chat/`
  }),
  actions: {
    async asyncGetAllApplication() {
      return new Promise((resolve, reject) => {
        applicationApi
          .getAllAppilcation()
          .then((data) => {
            resolve(data)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },

    async asyncGetApplicationDetail(id: string, loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        applicationApi
          .getApplicationDetail(id, loading)
          .then((data) => {
            resolve(data)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },

    async asyncGetApplicationDataset(id: string, loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        applicationApi
          .getApplicationDataset(id, loading)
          .then((data) => {
            resolve(data)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },

    async asyncGetAccessToken(id: string, loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        const user = useUserStore()
        if (user.isEnterprise()) {
          applicationXpackApi
            .getAccessToken(id, loading)
            .then((data) => {
              resolve(data)
            })
            .catch((error) => {
              reject(error)
            })
        } else {
          applicationApi
            .getAccessToken(id, loading)
            .then((data) => {
              resolve(data)
            })
            .catch((error) => {
              reject(error)
            })
        }
      })
    },

    async asyncGetAppProfile(loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        applicationApi
          .getAppProfile(loading)
          .then((res) => {
            sessionStorage.setItem('language', res.data?.language || getBrowserLang())
            resolve(res)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },

    async asyncAppAuthentication(
      token: string,
      loading?: Ref<boolean>,
      authentication_value?: any
    ) {
      return new Promise((resolve, reject) => {
        applicationApi
          .postAppAuthentication(token, loading, authentication_value)
          .then((res) => {
            localStorage.setItem(`${token}-accessToken`, res.data)
            sessionStorage.setItem(`${token}-accessToken`, res.data)
            resolve(res)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },
    async refreshAccessToken(token: string) {
      this.asyncAppAuthentication(token)
    },
    // 修改应用
    async asyncPutApplication(id: string, data: any, loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        applicationApi
          .putApplication(id, data, loading)
          .then((data) => {
            resolve(data)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },
    async validatePassword(id: string, password: string, loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        applicationApi
          .validatePassword(id, password, loading)
          .then((data) => {
            resolve(data)
          })
          .catch((error) => {
            reject(error)
          })
      })
    }
  }
})

export default useApplicationStore
