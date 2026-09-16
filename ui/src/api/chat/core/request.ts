/** 提供 Chat API 的 Axios 实例与常用 HTTP 请求封装。 */

import axios, { AxiosHeaders, type AxiosResponse, type InternalAxiosRequestConfig } from 'axios'
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

export default request
