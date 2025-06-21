import { defineStore } from 'pinia'
import type { knowledgeData } from '@/api/type/knowledge'
import type { UploadUserFile } from 'element-plus'
import knowledgeApi from '@/api/system-shared/knowledge'
import { type Ref } from 'vue'

export interface knowledgeStateTypes {
  baseInfo: knowledgeData | null
  webInfo: any
  documentsType: string
  documentsFiles: UploadUserFile[]
}

const useKnowledgeStore = defineStore('knowledg', {
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
    async asyncGetFolderKnowledge(loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        const params = {
          folder_id: 'default',
        }
        knowledgeApi
          .getKnowledgeList(params, loading)
          .then((data) => {
            resolve(data)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },
    async asyncGetKnowledgeDetail(knowledge_id: string, loading?: Ref<boolean>) {
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
  },
})

export default useKnowledgeStore
