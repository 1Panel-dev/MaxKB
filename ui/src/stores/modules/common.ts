import { defineStore } from 'pinia'

const useCommonStore = defineStore({
  id: 'common',
  state: () => ({
    breadcrumb: null
  }),
  actions: {
    saveBreadcrumb(data: any) {
      this.breadcrumb = data
    }
  }
})

export default useCommonStore
