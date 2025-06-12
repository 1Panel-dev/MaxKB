import { defineStore } from 'pinia'
import paragraphApi from '@/api/shared/paragraph'
import type { Ref } from 'vue'

const useParagraphStore = defineStore('paragrap', {
  state: () => ({}),
  actions: {
    async asyncPutParagraph(
      knowledgeId: string,
      documentId: string,
      paragraphId: string,
      data: any,
      loading?: Ref<boolean>,
    ) {
      return new Promise((resolve, reject) => {
        paragraphApi
          .putParagraph(knowledgeId, documentId, paragraphId, data, loading)
          .then((data) => {
            resolve(data)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },

    async asyncDelParagraph(
      knowledgeId: string,
      documentId: string,
      paragraphId: string,
      loading?: Ref<boolean>,
    ) {
      return new Promise((resolve, reject) => {
        paragraphApi
          .delParagraph(knowledgeId, documentId, paragraphId, loading)
          .then((data) => {
            resolve(data)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },
    async asyncDisassociationProblem(
      knowledgeId: string,
      documentId: string,
      paragraphId: string,
      problemId: string,
      loading?: Ref<boolean>,
    ) {
      return new Promise((resolve, reject) => {
        const obj = {
          paragraphId,
          problemId,
        }
        paragraphApi
          .putDisassociationProblem(knowledgeId, documentId, obj, loading)
          .then((data) => {
            resolve(data)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },
    async asyncAssociationProblem(
      knowledgeId: string,
      documentId: string,
      paragraphId: string,
      problemId: string,
      loading?: Ref<boolean>,
    ) {
      return new Promise((resolve, reject) => {
        const obj = {
          paragraphId,
          problemId,
        }
        paragraphApi
          .putAssociationProblem(knowledgeId, documentId, obj, loading)
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

export default useParagraphStore
