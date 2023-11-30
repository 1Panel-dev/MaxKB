import { defineStore } from 'pinia'
import type { datasetData } from '@/api/type/dataset'
import type { UploadUserFile } from 'element-plus'
import datasetApi from '@/api/dataset'
import { type Ref } from 'vue'

export interface datasetStateTypes {
  baseInfo: datasetData | null
  documentsFiles: UploadUserFile[]
}

const useDatasetStore = defineStore({
  id: 'dataset',
  state: (): datasetStateTypes => ({
    baseInfo: null,
    documentsFiles: []
  }),
  actions: {
    saveBaseInfo(info: datasetData | null) {
      this.baseInfo = info
    },
    saveDocumentsFile(file: UploadUserFile[]) {
      this.documentsFiles = file
    },
    async asyncGetAllDateset(loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        datasetApi
          .getAllDateset(loading)
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

export default useDatasetStore
