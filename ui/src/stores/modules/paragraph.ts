import { defineStore } from 'pinia'
import paragraphApi from '@/api/paragraph'

const useParagraphStore = defineStore({
  id: 'paragraph',
  state: () => ({}),
  actions: {
    async asyncPutParagraph(datasetId: string, documentId: string, paragraphId: string, data: any) {
      return new Promise((resolve, reject) => {
        paragraphApi
          .putParagraph(datasetId, documentId, paragraphId, data)
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
