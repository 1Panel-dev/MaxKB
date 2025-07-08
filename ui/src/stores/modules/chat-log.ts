import { defineStore } from 'pinia'
import chatLogApi from '@/api/application/chat-log'
import { type Ref } from 'vue'
import type { pageRequest } from '@/api/type/common'

const useChatLogStore = defineStore('chatLog',{
  state: () => ({}),
  actions: {
    async asyncGetChatLog(id: string, page: pageRequest, param: any, loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        chatLogApi
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
        chatLogApi
          .getChatRecordLog(id, chatId, page, loading, order_asc)
          .then((data) => {
            resolve(data)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },
  }
})

export default useChatLogStore
