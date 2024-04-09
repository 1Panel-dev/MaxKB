import { defineStore } from 'pinia'
import { type Ref } from 'vue'
import problemApi from '@/api/problem'
import paragraphApi from '@/api/paragraph'
import type { pageRequest } from '@/api/type/common'

const useProblemStore = defineStore({
  id: 'problem',
  state: () => ({}),
  actions: {
    async asyncPostProblem(datasetId: string, data: any, loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        problemApi
          .postProblems(datasetId, data, loading)
          .then((data) => {
            resolve(data)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },
    async asyncGetProblem(
      datasetId: string,
      page: pageRequest,
      param: any,
      loading?: Ref<boolean>
    ) {
      return new Promise((resolve, reject) => {
        problemApi
          .getProblems(datasetId, page, param, loading)
          .then((data) => {
            resolve(data)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },
    async asyncDisassociationProblem(
      datasetId: string,
      documentId: string,
      paragraphId: string,
      problemId: string,
      loading?: Ref<boolean>
    ) {
      return new Promise((resolve, reject) => {
        paragraphApi
          .disassociationProblem(datasetId, documentId, paragraphId, problemId, loading)
          .then((data) => {
            resolve(data)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },
    async asyncAssociationProblem(
      datasetId: string,
      documentId: string,
      paragraphId: string,
      problemId: string,
      loading?: Ref<boolean>
    ) {
      return new Promise((resolve, reject) => {
        paragraphApi
          .associationProblem(datasetId, documentId, paragraphId, problemId, loading)
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

export default useProblemStore
