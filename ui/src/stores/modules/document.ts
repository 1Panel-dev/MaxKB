import { defineStore } from 'pinia'
import { type Ref } from 'vue'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'

const useDocumentStore = defineStore('document', {
  state: () => ({}),
  actions: {
    async asyncGetKnowledgeDocument(
      id: string,
      systemType: 'systemShare' | 'workspace' | 'systemManage' = 'workspace',
      loading?: Ref<boolean>,
    ) {
      return new Promise((resolve, reject) => {
        loadSharedApi({ type: 'document', systemType })
          .getDocumentList(id, loading)
          .then((res: any) => {
            resolve(res)
          })
          .catch((error: any) => {
            reject(error)
          })
      })
    },
  },
})

export default useDocumentStore
