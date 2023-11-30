import { defineStore } from 'pinia'
import applicationApi from '@/api/application'
import { type Ref } from 'vue'

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

    async asyncAppAuthentication(token: string, loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        applicationApi
          .postAppAuthentication(token, loading)
          .then((res) => {
            localStorage.setItem('accessToken', res.data)
            resolve(res)
          })
          .catch((error) => {
            reject(error)
          })
      })
    }
  }
})

export default useApplicationStore
