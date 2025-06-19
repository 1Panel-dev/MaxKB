import { defineStore } from 'pinia'
import documentApi from '@/api/knowledge/document'
import { type Ref } from 'vue'

const useDocumentStore = defineStore('document', {
  state: () => ({}),
  actions: {
    async asyncGetKnowledgeDocument(id: string, loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        documentApi
          .getDocumentList(id, loading)
          .then((res) => {
            resolve(res)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },
    async asyncPutDocument(knowledgeId: string, data: any, loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        documentApi
          .putMulDocument(knowledgeId, data, loading)
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
