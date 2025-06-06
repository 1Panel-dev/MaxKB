import {defineStore} from 'pinia'
import type {knowledgeData} from '@/api/type/knowledge'
import type {UploadUserFile} from 'element-plus'
import knowledgeApi from '@/api/knowledge/knowledge'
import {type Ref} from 'vue'

export interface knowledgeStateTypes {
  baseInfo: knowledgeData | null
  webInfo: any
  documentsType: string
  documentsFiles: UploadUserFile[]
}

const useKnowledgeStore = defineStore('knowledge', {
  state: (): knowledgeStateTypes => ({
    baseInfo: null,
    webInfo: null,
    documentsType: '',
    documentsFiles: [],
  }),
  actions: {
    saveBaseInfo(info: knowledgeData | null) {
      this.baseInfo = info
    },
    saveWebInfo(info: any) {
      this.webInfo = info
    },
    saveDocumentsType(val: string) {
      this.documentsType = val
    },
    saveDocumentsFile(file: UploadUserFile[]) {
      this.documentsFiles = file
    },
    // async asyncGetAllDataset(loading?: Ref<boolean>) {
    //   return new Promise((resolve, reject) => {
    //     knowledgeApi
    //       .getAllDataset(loading)
    //       .then((data) => {
    //         resolve(data)
    //       })
    //       .catch((error) => {
    //         reject(error)
    //       })
    //   })
    // },
    async asyncGetDatasetDetail(
      knowledge_id: string,
      loading?: Ref<boolean>,
    ) {
      return new Promise((resolve, reject) => {
        knowledgeApi
          .getKnowledgeDetail(knowledge_id, loading)
          .then((data) => {
            resolve(data)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },
    async asyncSyncDataset(
      id: string,
      sync_type: string,
      loading?: Ref<boolean>,
    ) {
      return new Promise((resolve, reject) => {
        knowledgeApi
          .putSyncWebKnowledge(id, sync_type, loading)
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

export default useKnowledgeStore
