import { defineStore } from 'pinia'
import applicationApi from '@/api/application/application'
import applicationXpackApi from '@/api/application/application-xpack'
import { type Ref } from 'vue'
import useUserStore from './user'
const useApplicationStore = defineStore('application', {
  state: () => ({
    location: `${window.location.origin}${window.MaxKB.chatPrefix}/`,
  }),
  actions: {

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

    async asyncGetAccessToken(id: string, loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        const user = useUserStore()
        // if (user.isEE() || user.isPE()) {
        //   applicationXpackApi
        //     .getAccessToken(id, loading)
        //     .then((data) => {
        //       resolve(data)
        //     })
        //     .catch((error) => {
        //       reject(error)
        //     })
        // } else {
          applicationApi
            .getAccessToken(id, loading)
            .then((data) => {
              resolve(data)
            })
            .catch((error) => {
              reject(error)
            })
        // }
      })
    },

    async asyncAppAuthentication(
      token: string,
      loading?: Ref<boolean>,
      authentication_value?: any,
    ) {
      return new Promise((resolve, reject) => {
        applicationApi
          .postAppAuthentication(token, loading, authentication_value)
          .then((res: any) => {
            localStorage.setItem(`${token}-accessToken`, res.data)
            sessionStorage.setItem(`${token}-accessToken`, res.data)
            resolve(res)
          })
          .catch((error: any) => {
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
  },
})

export default useApplicationStore
