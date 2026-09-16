/** Chat 请求基础设施内部使用的协议类型。 */

export interface ApiResponse<T> {
  code: number
  message: string
  data: T
}

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
