import { defineStore } from 'pinia'
import documentApi from '@/api/knowledge/document'
import { type Ref } from 'vue'

const useDocumentStore = defineStore('document', {
  state: () => ({}),
  actions: {
    async asyncGetAllDocument(id: string, loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        documentApi
          .getAllDocument(id, loading)
          .then((res) => {
            resolve(res)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },
    async asyncPostDocument(knowledgeId: string, data: any, loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        documentApi
          .postDocument(knowledgeId, data, loading)
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

export default useDocumentStore
