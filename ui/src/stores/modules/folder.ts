import { defineStore } from 'pinia'
import { type Ref } from 'vue'
import folderApi from '@/api/folder'

const useFolderStore = defineStore('folder', {
  state: () => ({
    currentFolder: {} as any,
  }),
  actions: {
    setCurrentFolder(folder: any) {
      this.currentFolder = folder
    },
    async asyncGetFolder(source: string, data: any, loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        folderApi
          .getFolder(source, data, loading)
          .then((res) => {
            resolve(res)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },
  },
})

export default useFolderStore
