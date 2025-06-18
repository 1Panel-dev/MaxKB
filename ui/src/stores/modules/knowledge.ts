import { defineStore } from 'pinia'
import type { knowledgeData } from '@/api/type/knowledge'
import type { UploadUserFile } from 'element-plus'
import knowledgeApi from '@/api/knowledge/knowledge'
import { type Ref } from 'vue'
import useFolderStore from './folder'

export interface knowledgeStateTypes {
  baseInfo: knowledgeData | null
  webInfo: any
  documentsType: string
  documentsFiles: UploadUserFile[]
}

const useKnowledgeStore = defineStore('knowledge', {
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
    async asyncGetRootKnowledge(loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        const params = {
          folder_id: localStorage.getItem('workspace_id'),
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
    async asyncGetTreeRootKnowledge(loading?: Ref<boolean>) {
      const folder = useFolderStore()
      return Promise.all([
        folder.asyncGetFolder('KNOWLEDGE', {}, loading),
        this.asyncGetRootKnowledge(loading),
      ])
        .then((res: any) => {
          const folderList = res[0].data
          const knowledgeList = res[1].data
          const arrMap: any = {}
          function buildIdMap(arr: any) {
            arr.forEach((item: any) => {
              arrMap[item.id] = item
              // 递归处理子节点
              if (item.children && item.children.length > 0) {
                buildIdMap(item.children)
              }
            })
          }
          buildIdMap(folderList)
          knowledgeList
            .filter((v: any) => v.resource_type !== 'folder')
            .forEach((item: any) => {
              const targetFolder = arrMap[item.folder_id]
              if (targetFolder) {
                // 检查是否已有相同ID的子节点（避免重复插入）
                const existingChild = targetFolder.children.find(
                  (child: any) => child.id === item.id,
                )
                if (!existingChild) {
                  targetFolder.children.push(item)
                }
              }
            })
          return Promise.resolve(folderList)
        })
        .catch((error) => {
          return Promise.reject(error)
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
