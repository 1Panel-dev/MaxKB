import { defineStore } from 'pinia'
import applicationApi from '@/api/application/application'
import { type Ref } from 'vue'
const useApplicationStore = defineStore('application', {
  state: () => ({
    location: `${window.location.origin}${window.MaxKB.chatPrefix ? window.MaxKB.chatPrefix : window.MaxKB.prefix}/`,
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
        applicationApi
          .getAccessToken(id, loading)
          .then((data) => {
            resolve(data)
          })
          .catch((error) => {
            reject(error)
          })
      })
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
