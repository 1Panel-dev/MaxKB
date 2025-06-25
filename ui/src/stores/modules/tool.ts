import { defineStore } from 'pinia'
import { type Ref } from 'vue'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import type { pageRequest } from '@/api/type/common'
import useUserStore from './user'
import useFolderStore from './folder'

const useToolStore = defineStore('tool', {
  state: () => ({
    toolList: [] as any[],
  }),
  actions: {
    setToolList(list: any[]) {
      this.toolList = list
    },
  },
})

export default useToolStore
