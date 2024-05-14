import { defineStore } from 'pinia'
import logApi from '@/api/log'
import { type Ref } from 'vue'
import type { pageRequest } from '@/api/type/common'

const useLogStore = defineStore({
  id: 'log',
  state: () => ({}),
  actions: {
    async asyncGetChatLog(id: string, page: pageRequest, param: any, loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        logApi
          .getChatLog(id, page, param, loading)
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

export default useLogStore
