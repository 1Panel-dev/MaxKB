/** 提供 Chat API 的 Axios 实例与常用 HTTP 请求封装。 */

import axios, { AxiosHeaders, type AxiosResponse, type AxiosProgressEvent, type InternalAxiosRequestConfig } from 'axios'
import { useStore } from '@/stores'
import type { ApiResponse } from './types'
import type { Dict } from '@/api/types'
import { MsgError } from '@/utils/message'
import { CHAT_API_BASE_PATH } from '@/api/constants'

const DEFAULT_TIMEOUT = 30 * 60 * 1_000 // 30 minutes

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
  baseURL: CHAT_API_BASE_PATH,
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
    if (axios.isCancel(error)) {
      return Promise.reject(error)
    }

    if (!axios.isAxiosError<ApiResponse<unknown>>(error)) {
      return Promise.reject(error)
    }

    const responseMessage = await getResponseErrorMessage(error)
    MsgError(responseMessage || error.message)
    return Promise.reject(error)
  },
)

/**
 * 统一解包标准 API 响应。
 */
export async function promise<T>(requestPromise: Promise<AxiosResponse<ApiResponse<T>>>) {
  const response = await requestPromise
  return response.data.data
}

/** 发送 GET 请求。 */
export function get<T = unknown>(url: string, params?: Dict<unknown>, timeout?: number) {
  return promise<T>(request.get<ApiResponse<T>>(url, { params, timeout }))
}

/** 发送 POST 请求。 */
export function post<TData = unknown, T = unknown>(url: string, data?: TData, params?: Dict<unknown>, timeout?: number) {
  return promise<T>(request.post<ApiResponse<T>>(url, data, { params, timeout }))
}

/** 发送 PUT 请求。 */
export function put<TData = unknown, T = unknown>(url: string, data?: TData, params?: Dict<unknown>, timeout?: number) {
  return promise<T>(request.put<ApiResponse<T>>(url, data, { params, timeout }))
}

/** 发送 DELETE 请求。 */
export function del<TData = unknown, T = unknown>(url: string, params?: Dict<unknown>, data?: TData, timeout?: number) {
  return promise<T>(request.delete<ApiResponse<T>>(url, { params, data, timeout }))
}

/** 发送流式 POST 请求，返回原始 `Response` 供 SSE 读取。 */
export function postStream(base: string, path: string, data?: unknown) {
  const { auth, user } = useStore()
  const headers: Record<string, string> = { 'Content-Type': 'application/json' }
  if (auth.token) {
    headers['Authorization'] = `Bearer ${auth.token}`
  }
  if (user.language) {
    headers['Accept-Language'] = user.language
  }
  return fetch(`${base}${path.startsWith('/') ? path : `/${path}`}`, {
    method: 'POST',
    headers,
    body: data === undefined ? undefined : JSON.stringify(data),
  })
}

/** 上传文件，支持进度回调与取消，响应统一解包。 */
export function postUpload<T = unknown>(url: string, data: FormData, onProgress?: (percent: number, event: AxiosProgressEvent) => void) {
  const controller = new AbortController()
  const uploadRequest = promise<T>(
    request.post<ApiResponse<T>>(url, data, {
      signal: controller.signal,
      onUploadProgress: onProgress
        ? (event) => {
            if (event.total && event.total > 0) {
              onProgress(Math.min(100, Math.max(0, Math.round((event.loaded / event.total) * 100))), event)
            }
          }
        : undefined,
    }),
  )
  return { request: uploadRequest, abort: () => controller.abort() }
}

export default request
