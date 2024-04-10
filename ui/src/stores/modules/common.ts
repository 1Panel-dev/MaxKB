import { defineStore } from 'pinia'

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
    paginationConfig: {},
    search: {}
  }),
  actions: {
    saveBreadcrumb(data: any) {
      this.breadcrumb = data
    },
    savePage(val: string, data: any) {
      this.paginationConfig[val] = data
    },
    saveCondition(val: string, data: any) {
      this.search[val] = data
    }
  }
})

export default useCommonStore
