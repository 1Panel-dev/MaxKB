import { defineStore } from 'pinia'
import modelApi from '@/api/model'
import type { ListModelRequest, Provider } from '@/api/type/model'
const useModelStore = defineStore({
  id: 'model',
  state: () => ({}),
  actions: {
    async asyncGetModel(data?: ListModelRequest) {
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
