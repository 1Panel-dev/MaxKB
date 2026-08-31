/**
 * 智能体详情子路由的共享上下文契约。
 * 子页面只读取容器持有的详情；保存接口返回完整详情时直接替换，返回布尔值或部分数据时重新请求，
 * 避免依赖父容器重新挂载来同步标题、图标和其他子页面共用的数据。
 */

import { inject, type ComputedRef, type InjectionKey } from 'vue'
import type { ApplicationDetail } from '@/api/types'

export interface ApplicationDetailContext {
  /** 当前共享详情，子页面不能直接替换其引用。 */
  application: ComputedRef<ApplicationDetail | undefined>
  /** 重新请求当前 applicationId 的完整详情。 */
  refreshApplicationDetail: () => Promise<void>
  /** 使用接口返回的完整详情更新上下文，避免额外请求。 */
  replaceApplicationDetail: (applicationDetail: ApplicationDetail) => void
}

export const applicationDetailContextKey: InjectionKey<ApplicationDetailContext> = Symbol('application-detail-context')

export function useApplicationDetailContext() {
  const applicationDetailContext = inject(applicationDetailContextKey)
  if (!applicationDetailContext) throw new Error('Application detail context is unavailable')

  return applicationDetailContext
}
