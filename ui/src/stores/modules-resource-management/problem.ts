import { defineStore } from 'pinia'
import { type Ref } from 'vue'
import problemApi from '@/api/resource-management/problem'
import type { pageRequest } from '@/api/type/common'

const useProblemStore = defineStore('probl', {
  state: () => ({}),
  actions: {
    async asyncPostProblem(knowledgeId: string, data: any, loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        problemApi
          .postProblems(knowledgeId, data, loading)
          .then((data) => {
            resolve(data)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },
    async asyncGetProblem(
      knowledgeId: string,
      page: pageRequest,
      param: any,
      loading?: Ref<boolean>,
    ) {
      return new Promise((resolve, reject) => {
        problemApi
          .getProblems(knowledgeId, page, param, loading)
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

export default useProblemStore
