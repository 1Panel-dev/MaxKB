import { defineStore } from 'pinia'
import type { User } from '@/api/type/user'
import UserApi from '@/api/user'

const useCommonStore = defineStore({
  id: 'common',
  state: () => ({
    breadcrumb: null
  }),
  actions: {
    saveBreadcrumb(data) {
      this.breadcrumb = data
    }
  }
})

export default useCommonStore
