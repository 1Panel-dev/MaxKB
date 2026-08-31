/** 提供 Chat API 的 Axios 实例与常用 HTTP 请求封装。 */

import axios, {
  AxiosHeaders,
  type AxiosResponse,
  type InternalAxiosRequestConfig,
} from 'axios'
import { useStore } from '@/stores'
import type { ApiResponse, LoadingTarget } from './types'
import type { Dict } from '@/api/types'
import { MsgError } from '@/utils/message'

const DEFAULT_TIMEOUT = 30 * 60 * 1_000 // 30 minutes
const CHAT_BASE_PATH = window.MaxKB?.chatPrefix || import.meta.env.VITE_BASE_PATH || '/chat/'

function setRequestHeaders(config: InternalAxiosRequestConfig) {
  const { auth, user } = useStore()

  if (!(config.headers instanceof AxiosHeaders)) {
    config.headers = new AxiosHeaders(config.headers)
  }
  if (auth.token) {
    config.headers.set('Authorization', `Bearer ${auth.token}`)
  }
  if (user.language) {
    config.headers.set('Accept-Language', user.language)
  }

  return config
}

function startLoading(loading?: LoadingTarget) {
  if (!loading) {
    return
  }
  if ('start' in loading) {
    loading.start()
    return
  }
  loading.value = true
}

function finishLoading(loading?: LoadingTarget) {
  if (!loading) {
    return
  }
  if ('done' in loading) {
    loading.done()
    return
  }
  loading.value = false
}

async function getResponseErrorMessage(error: unknown) {
  if (!axios.isAxiosError<ApiResponse<unknown> | string>(error)) {
    return undefined
  }

  const responseData = error.response?.data
  if (typeof responseData === 'string') {
    return responseData
  }
  return responseData?.message
}

export const request = axios.create({
  baseURL: `${CHAT_BASE_PATH.replace(/\/+$/, '')}/api`,
  timeout: DEFAULT_TIMEOUT,
  withCredentials: false,
})

request.interceptors.request.use(setRequestHeaders)

request.interceptors.response.use(
  (response) => {
    const responseData = response.data as ApiResponse<unknown>
    if (responseData.code !== 200) {
      MsgError(responseData.message)
      return Promise.reject(responseData)
    }
    return response
  },
  async (error: unknown) => {
    if (!axios.isAxiosError<ApiResponse<unknown>>(error)) {
      return Promise.reject(error)
    }

    const responseMessage = await getResponseErrorMessage(error)
    MsgError(responseMessage || error.message)
    return Promise.reject(error)
  },
)

/**
 * 统一解包标准 API 响应，并同步可选的 loading 状态。
 */
export async function promise<T>(
  requestPromise: Promise<AxiosResponse<ApiResponse<T>>>,
  loading?: LoadingTarget,
) {
  startLoading(loading)
  try {
    const response = await requestPromise
    return response.data.data
  } finally {
    finishLoading(loading)
  }
}

/** 发送 GET 请求。 */
export function get<T = unknown>(
  url: string,
  params?: Dict<unknown>,
  loading?: LoadingTarget,
  timeout?: number,
) {
  return promise<T>(request.get<ApiResponse<T>>(url, { params, timeout }), loading)
}

/** 发送 POST 请求。 */
export function post<TData = unknown, T = unknown>(
  url: string,
  data?: TData,
  params?: Dict<unknown>,
  loading?: LoadingTarget,
  timeout?: number,
) {
  return promise<T>(request.post<ApiResponse<T>>(url, data, { params, timeout }), loading)
}

/** 发送 PUT 请求。 */
export function put<TData = unknown, T = unknown>(
  url: string,
  data?: TData,
  params?: Dict<unknown>,
  loading?: LoadingTarget,
  timeout?: number,
) {
  return promise<T>(request.put<ApiResponse<T>>(url, data, { params, timeout }), loading)
}

/** 发送 DELETE 请求。 */
export function del<TData = unknown, T = unknown>(
  url: string,
  params?: Dict<unknown>,
  data?: TData,
  loading?: LoadingTarget,
  timeout?: number,
) {
  return promise<T>(request.delete<ApiResponse<T>>(url, { params, data, timeout }), loading)
}

export default request
