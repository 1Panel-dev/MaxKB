import { defineStore } from 'pinia'
import { DeviceType, ValidType } from '@/enums/common'
import type { Ref } from 'vue'
import userApi from '@/api/user'

export interface commonTypes {
  breadcrumb: any
  paginationConfig: any | null
  search: any
  device: string
}

const useCommonStore = defineStore({
  id: 'common',
  state: (): commonTypes => ({
    breadcrumb: null,
    // 搜索和分页缓存
    paginationConfig: {},
    search: {},
    device: DeviceType.Desktop
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
    },
    toggleDevice(value: DeviceType) {
      this.device = value
    },
    isMobile() {
      return this.device === DeviceType.Mobile
    },
    async asyncGetValid(valid_type: ValidType, valid_count: number, loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        userApi
          .getValid(valid_type, valid_count, loading)
          .then((data) => {
            resolve(data)
          })
          .catch((error) => {
            reject(error)
          })
      })
    }
  }
})

export default useCommonStore
