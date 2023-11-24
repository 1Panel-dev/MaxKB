import { defineStore } from 'pinia'
import modelApi from '@/api/model'
import type { modelRequest, Provider } from '@/api/type/model'
const useModelStore = defineStore({
  id: 'model',
  state: () => ({}),
  actions: {
    async asyncGetModel(data?: modelRequest) {
      return new Promise((resolve, reject) => {
        modelApi
          .getModel(data)
          .then((res) => {
            resolve(res)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },
    async asyncGetProvider() {
      return new Promise((resolve, reject) => {
        modelApi
          .getProvider()
          .then((res) => {
            resolve(res)
          })
          .catch((error) => {
            reject(error)
          })
      })
    }
  }
})

export default useModelStore
