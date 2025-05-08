import { defineStore } from 'pinia'
import { type Ref } from 'vue'
import folderApi from '@/api/folder'

const useFolderStore = defineStore('folder', {
  state: () => ({}),
  actions: {
    async asynGetFolder(workspace_id: string, source: string, data: any, loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        folderApi
          .getFolder(workspace_id, source, data, loading)
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
