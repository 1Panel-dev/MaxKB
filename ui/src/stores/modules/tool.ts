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
    async asyncGetToolListPage(
      page: pageRequest,
      isShared: boolean | undefined,
      systemType: 'systemShare' | 'workspace' | 'systemManage' = 'workspace',
      paramsData: any,
      loading?: Ref<boolean>,
    ) {
      return new Promise((resolve, reject) => {
        const folder = useFolderStore()
        const user = useUserStore()
        const params = {
          folder_id: folder.currentFolder?.id || user.getWorkspaceId(),
          scope: systemType === 'systemShare' ? 'SHARED' : 'WORKSPACE',
          ...paramsData,
        }
        loadSharedApi({ type: 'tool', isShared, systemType })
          .getToolListPage(page, params, loading)
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

export default useToolStore
