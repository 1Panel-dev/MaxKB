/** 提供应用 Pinia 实例和组件外的统一 Store 访问入口。 */

import { createPinia } from 'pinia'
import { useAuthStore } from './auth'
import { useThemeStore } from './theme'
import { useUserStore } from './user'

export const pinia = createPinia()

const stores = {
  get auth() {
    return useAuthStore(pinia)
  },
  get user() {
    return useUserStore(pinia)
  },
  get theme() {
    return useThemeStore(pinia)
  },
}

/** 在 Router、Axios 等组件外代码中按需访问应用 Store。 */
export function useStore() {
  return stores
}
