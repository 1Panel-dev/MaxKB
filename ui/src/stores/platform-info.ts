/** 管理平台版本、许可和登录加密公钥等公开信息。 */

import { defineStore } from 'pinia'
import platformInfoApi from '@/api/admin/auth/platform-info'
import type { PlatformInfo } from '@/types'

interface PlatformInfoState {
  platformInfo: PlatformInfo | null
}

export const usePlatformInfoStore = defineStore('platformInfo', {
  state: (): PlatformInfoState => ({
    platformInfo: null,
  }),

  getters: {
    showXpack: (state) => Boolean(state.platformInfo && state.platformInfo.edition !== 'CE'),
    isExpire: (state) =>
      Boolean(
        state.platformInfo &&
        state.platformInfo.edition !== 'CE' &&
        !state.platformInfo.license_is_valid,
      ),
    isCE: (state) => state.platformInfo?.edition === 'CE',
    isPE: (state) => state.platformInfo?.edition === 'PE' && state.platformInfo.license_is_valid,
    isEE: (state) => state.platformInfo?.edition === 'EE' && state.platformInfo.license_is_valid,
    isPremium(): boolean {
      return this.isPE || this.isEE
    },
  },

  actions: {
    /** 加载并保存登录前所需的平台公开信息。 */
    loadPlatformInfo() {
      if (this.platformInfo) return Promise.resolve(this.platformInfo)
      return platformInfoApi.getPlatformInfo().then((platformInfo) => {
        this.platformInfo = platformInfo
        return platformInfo
      })
    },
  },
})
