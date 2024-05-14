import { defineStore } from 'pinia'
import paragraphApi from '@/api/paragraph'
import type { Ref } from 'vue'

const useParagraphStore = defineStore({
  id: 'paragraph',
  state: () => ({}),
  actions: {
    async asyncPutParagraph(
      datasetId: string,
      documentId: string,
      paragraphId: string,
      data: any,
      loading?: Ref<boolean>
    ) {
      return new Promise((resolve, reject) => {
        paragraphApi
          .putParagraph(datasetId, documentId, paragraphId, data, loading)
          .then((data) => {
            resolve(data)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },

    async asyncDelParagraph(
      datasetId: string,
      documentId: string,
      paragraphId: string,
      loading?: Ref<boolean>
    ) {
      return new Promise((resolve, reject) => {
        paragraphApi
          .delParagraph(datasetId, documentId, paragraphId, loading)
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

export default useParagraphStore
