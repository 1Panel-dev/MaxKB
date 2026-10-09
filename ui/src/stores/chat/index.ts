/** 提供 Chat 入口的 Pinia 实例和组件外的统一 Store 访问入口。 */

import { createPinia } from 'pinia'
import { useChatAuthStore } from './auth'
import { useChatUserStore } from './user'

export const pinia = createPinia()

const stores = {
  get auth() {
    return useChatAuthStore(pinia)
  },
  get user() {
    return useChatUserStore(pinia)
  },
}

/** 在 Router、Axios 等组件外代码中按需访问 Chat Store。 */
export function useStore() {
  return stores
}
