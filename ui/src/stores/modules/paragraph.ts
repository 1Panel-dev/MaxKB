import { defineStore } from 'pinia'
import datasetApi from '@/api/dataset'

const useParagraphStore = defineStore({
  id: 'paragraph',
  state: () => ({}),
  actions: {
    async asyncPutParagraph(datasetId: string, documentId: string, paragraphId: string, data: any) {
      return new Promise((resolve, reject) => {
        datasetApi
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
