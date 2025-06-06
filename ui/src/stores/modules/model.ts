import {defineStore} from 'pinia'
import {type Ref} from 'vue'
import ModelApi from '@/api/model/model'
import ProviderApi from '@/api/model/provider'
import type {ListModelRequest} from '@/api/type/model'

const useModelStore = defineStore('model', {
  state: () => ({}),
  actions: {
    async asyncGetModel(data?: ListModelRequest, loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        ModelApi.getModel(data, loading)
          .then((res) => {
            resolve(res)
          })
          .catch((error) => {
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
