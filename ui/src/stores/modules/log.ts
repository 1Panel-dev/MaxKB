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
    },
    async asyncChatRecordLog(
      id: string,
      chatId: string,
      page: pageRequest,
      loading?: Ref<boolean>,
      order_asc?: boolean
    ) {
      return new Promise((resolve, reject) => {
        logApi
          .getChatRecordLog(id, chatId, page, loading, order_asc)
          .then((data) => {
            resolve(data)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },
    async asyncGetChatLogClient(id: string, page: pageRequest, loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        logApi
          .getChatLogClient(id, page, loading)
          .then((data) => {
            resolve(data)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },
    async asyncDelChatClientLog(id: string, chatId: string, loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        logApi
          .delChatClientLog(id, chatId, loading)
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
