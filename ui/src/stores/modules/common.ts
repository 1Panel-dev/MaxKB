import { defineStore } from 'pinia'
import type { pageRequest } from '@/api/type/common'

export interface commonTypes {
  breadcrumb: any
  paginationConfig: any | null
  search: any
}

const useCommonStore = defineStore({
  id: 'common',
  state: (): commonTypes => ({
    breadcrumb: null,
    // 搜索和分页缓存
    paginationConfig: null,
    search: null
  }),
  actions: {
    saveBreadcrumb(data: any) {
      this.breadcrumb = data
    },
    savePage(val: string, data: pageRequest) {
      this.paginationConfig[val] = data
    },
    saveCondition(val: string, data: any) {
      this.search[val] = data
    }
  }
})

export default useCommonStore
