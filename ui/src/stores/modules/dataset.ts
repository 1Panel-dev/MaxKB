import { defineStore } from 'pinia'
import type { datasetData } from '@/api/type/dataset'
import type { UploadUserFile } from 'element-plus'

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
    }
  }
})

export default useDatasetStore
