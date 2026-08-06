/** Admin 请求基础设施内部使用的协议和 loading 类型。 */

export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

export type RequestParams = Record<string, unknown>

interface LoadingRef {
  value: boolean
}

interface LoadingProgress {
  start(): void
  done(): void
}

export type LoadingTarget = LoadingRef | LoadingProgress
