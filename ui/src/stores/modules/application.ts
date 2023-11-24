import { defineStore } from 'pinia'
import applicationApi from '@/api/application'

const useApplicationStore = defineStore({
  id: 'application',
  state: () => ({}),
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
    }
  }
})

export default useApplicationStore
