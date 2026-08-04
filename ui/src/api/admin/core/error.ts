/** 定义 Admin API 请求失败时使用的标准错误。 */

export interface ApiErrorOptions {
  code?: number
  status?: number
  data?: unknown
  cause?: unknown
}

export class ApiError extends Error {
  readonly code?: number
  readonly status?: number
  readonly data?: unknown

  constructor(message: string, options: ApiErrorOptions = {}) {
    super(message, { cause: options.cause })
    this.name = 'ApiError'
    this.code = options.code
    this.status = options.status
    this.data = options.data
  }
}
