import { defineStore } from 'pinia'
import { type Ref } from 'vue'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'

const useFolderStore = defineStore('folder', {
  state: () => ({
    currentFolder: {} as any,
  }),
  actions: {
    setCurrentFolder(folder: any) {
      this.currentFolder = folder
    },
    async asyncGetFolder(source: string, data: any, systemType: any, loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        loadSharedApi({
          type: 'folder',
          systemType,
        })
          .getFolder(source, data, loading)
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

export default useFolderStore
