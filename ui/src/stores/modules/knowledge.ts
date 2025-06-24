import { defineStore } from 'pinia'
import type { knowledgeData } from '@/api/type/knowledge'
import type { UploadUserFile } from 'element-plus'
import type { pageRequest } from '@/api/type/common'
import { type Ref } from 'vue'
import useUserStore from './user'
import useFolderStore from './folder'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'
import knowledgeApi from '@/api/knowledge/knowledge'

export interface knowledgeStateTypes {
  baseInfo: knowledgeData | null
  webInfo: any
  documentsType: string
  documentsFiles: UploadUserFile[]
  knowledgeList: any[]
}

const useKnowledgeStore = defineStore('knowledge', {
  state: (): knowledgeStateTypes => ({
    baseInfo: null,
    webInfo: null,
    documentsType: '',
    documentsFiles: [],
    knowledgeList: [],
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
    setKnowledgeList(list: any[]) {
      this.knowledgeList = list
    },
    async asyncGetKnowledgeListPage(
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
        loadSharedApi({ type: 'knowledge', isShared, systemType })
          .getKnowledgeListPage(page, params, loading)
          .then((res: any) => {
            resolve(res)
          })
          .catch((error: any) => {
            reject(error)
          })
      })
    },
    async asyncGetFolderKnowledge(folder_id?: string, loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        const params = {
          folder_id: folder_id || localStorage.getItem('workspace_id'),
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
  },
})

export default useKnowledgeStore
