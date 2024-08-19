import { defineStore } from 'pinia'
import applicationApi from '@/api/application'
import applicationXpackApi from '@/api/application-xpack'
import { type Ref, type UnwrapRef } from 'vue'

import useUserStore from './user'
import type { ApplicationFormType } from '@/api/type/application'

const useApplicationStore = defineStore({
  id: 'application',
  state: () => ({
    location: `${window.location.origin}/ui/chat/`
  }),
  actions: {
    async asyncGetAllApplication() {
      return new Promise((resolve, reject) => {
        applicationApi
          .getAllAppilcation()
          .then((data) => {
            resolve(data)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },

    async asyncGetApplicationDetail(id: string, loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        applicationApi
          .getApplicationDetail(id, loading)
          .then((data) => {
            resolve(data)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },

    async asyncGetApplicationDataset(id: string, loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        applicationApi
          .getApplicationDataset(id, loading)
          .then((data) => {
            resolve(data)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },

    async asyncGetAccessToken(id: string, loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        const user = useUserStore()
        if (user.isEnterprise()) {
          applicationXpackApi
            .getAccessToken(id, loading)
            .then((data) => {
              resolve(data)
            })
            .catch((error) => {
              reject(error)
            })
        } else {
          applicationApi
            .getAccessToken(id, loading)
            .then((data) => {
              resolve(data)
            })
            .catch((error) => {
              reject(error)
            })
        }
      })
    },

    async asyncGetAppProfile(loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        const user = useUserStore()
        if (user.isEnterprise()) {
          applicationXpackApi
            .getAppXpackProfile(loading)
            .then((data) => {
              resolve(data)
            })
            .catch((error) => {
              reject(error)
            })
        } else {
          applicationApi
            .getAppProfile(loading)
            .then((data) => {
              resolve(data)
            })
            .catch((error) => {
              reject(error)
            })
        }
      })
    },

    async asyncAppAuthentication(token: string, loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        applicationApi
          .postAppAuthentication(token, loading)
          .then((res) => {
            localStorage.setItem('accessToken', res.data)
            sessionStorage.setItem('accessToken', res.data)
            resolve(res)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },
    async refreshAccessToken(token: string) {
      this.asyncAppAuthentication(token)
    },
    // 修改应用
    async asyncPutApplication(id: string, data: any, loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        applicationApi
          .putApplication(id, data, loading)
          .then((data) => {
            resolve(data)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },
    // 获取模型的  温度/max_token字段设置
    async asyncGetModelConfig(
      id: string,
      model_id: string,
      ai_node_id?: string,
      loading?: Ref<boolean>
    ) {
      return new Promise((resolve, reject) => {
        applicationApi
          .getModelOtherConfig(id, model_id, ai_node_id, loading)
          .then((data) => {
            resolve(data)
          })
          .catch((error) => {
            reject(error)
          })
      })
    },
    // 保存应用的  温度/max_token字段设置
    async asyncPostModelConfig(id: string, params?: any, loading?: Ref<boolean>) {
      return new Promise((resolve, reject) => {
        applicationApi
          .putModelOtherConfig(id, params, loading)
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

export default useApplicationStore
