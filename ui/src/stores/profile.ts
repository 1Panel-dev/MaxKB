/** 管理平台版本、许可和登录加密公钥等公开档案。 */

import { defineStore } from 'pinia'
import BaseInfoApi from '@/api/admin/auth/base-info'
import type { BaseProfile } from '@/api/admin/auth/types'

interface BaseProfileState {
  BaseProfile: BaseProfile | null
}

export const useProfileStore = defineStore('BaseProfile', {
  state: (): BaseProfileState => ({
    BaseProfile: null,
  }),

  getters: {
    showXpack: (state) => Boolean(state.BaseProfile && state.BaseProfile.edition !== 'CE'),
    isExpire: (state) =>
      Boolean(
        state.BaseProfile &&
        state.BaseProfile.edition !== 'CE' &&
        !state.BaseProfile.license_is_valid,
      ),
    isCE: (state) => state.BaseProfile?.edition === 'CE',
    isPE: (state) => state.BaseProfile?.edition === 'PE' && state.BaseProfile.license_is_valid,
    isEE: (state) => state.BaseProfile?.edition === 'EE' && state.BaseProfile.license_is_valid,
  },

  actions: {
    /** 加载并保存登录前所需的平台公开档案。 */
    loadBaseProfile() {
      return BaseInfoApi.getBaseProfile().then((BaseProfile) => {
        this.BaseProfile = BaseProfile
        return BaseProfile
      })
    },
  },
})
