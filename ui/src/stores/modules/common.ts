import { defineStore } from 'pinia'
import { DeviceType } from '@/enums/common'

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
    }
  }
})

export default useCommonStore
