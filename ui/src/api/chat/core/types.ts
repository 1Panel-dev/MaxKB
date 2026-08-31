/** Chat 请求基础设施内部使用的协议和 loading 类型。 */

export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

interface LoadingRef {
  value: boolean
}

interface LoadingProgress {
  start(): void
  done(): void
}

export type LoadingTarget = LoadingRef | LoadingProgress

export interface ResponsePage<T> {
  total: number
  records: T[]
  current: number
  size: number
}

export interface ParamsPage {
  currentPage: number
  pageSize: number
}
