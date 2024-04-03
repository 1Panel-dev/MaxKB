import { defineStore } from 'pinia'
import problemApi from '@/api/problem'
import { type Ref } from 'vue'

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
    }
  }
})

export default useProblemStore
