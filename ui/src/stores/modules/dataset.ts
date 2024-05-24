import { defineStore } from 'pinia'
import type { datasetData } from '@/api/type/dataset'
import type { UploadUserFile } from 'element-plus'
import datasetApi from '@/api/dataset'
import { type Ref } from 'vue'

export interface datasetStateTypes {
  baseInfo: datasetData | null
  webInfo: any
  documentsType: string
  documentsFiles: UploadUserFile[]
}

const useDatasetStore = defineStore({
  id: 'dataset',
  state: (): datasetStateTypes => ({
    baseInfo: null,
    webInfo: null,
    documentsType: '',
    documentsFiles: []
  }),
  actions: {
    saveBaseInfo(info: datasetData | null) {
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
    async asyncGetAllDataset(loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        datasetApi
          .getAllDataset(loading)
          .then((data) => {
            resolve(data)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },
    async asyncGetDatasetDetail(id: string, loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        datasetApi
          .getDatasetDetail(id, loading)
          .then((data) => {
            resolve(data)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },
    async asyncSyncDataset(id: string, sync_type: string, loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        datasetApi
          .putSyncWebDataset(id, sync_type, loading)
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
