import { defineStore } from 'pinia'
import { type Ref } from 'vue'
import ProviderApi from '@/api/model/provider'
import type { ListModelRequest } from '@/api/type/model'
import { loadSharedApi } from '@/utils/dynamics-api/shared-api'

const useModelStore = defineStore('model', {
  state: () => ({}),
  actions: {
    async asyncGetSelectModel(
      systemType: 'systemShare' | 'workspace' | 'systemManage' = 'workspace',
      data?: ListModelRequest,
      loading?: Ref<boolean>,
    ) {
      return new Promise((resolve, reject) => {
        loadSharedApi({ type: 'model', systemType })
          .getSelectModelList(data, loading)
          .then((res: any) => {
            resolve(res)
          })
          .catch((error: any) => {
            reject(error)
          })
      })
    },
    async asyncGetProvider(loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        ProviderApi.getProvider(loading)
          .then((res) => {
            resolve(res)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },
  },
})

export default useModelStore
