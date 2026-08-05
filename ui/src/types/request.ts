/** 请求基础设施使用的协议、分页和 loading 类型。 */

export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

export interface PageData<T> {
  total: number
  records: T[]
  current: number
  size: number
}

export type RequestParams = Record<string, unknown>

export interface LoadingRef {
  value: boolean
}

export interface LoadingProgress {
  start(): void
  done(): void
}

export type LoadingTarget = LoadingRef | LoadingProgress
