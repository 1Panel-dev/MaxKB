import axios, { type AxiosRequestConfig } from 'axios'
import { MsgError } from '@/utils/message'
import type { NProgress } from 'nprogress'
import type { Ref } from 'vue'
import type { Result } from '@/request/Result'
import useStore from '@/stores'
import router from '@/router'

import { ref, type WritableComputedRef } from 'vue'

const axiosConfig = {
  baseURL: '/api',
  withCredentials: false,
  timeout: 60000,
  headers: {}
}

const instance = axios.create(axiosConfig)

/* 设置请求拦截器 */
instance.interceptors.request.use(
  (config: AxiosRequestConfig) => {
    if (config.headers === undefined) {
      config.headers = {}
    }
    const { user } = useStore()
    const token = user.getToken()
    if (token) {
      config.headers['AUTHORIZATION'] = `${token}`
    }
    return config
  },
  (err: any) => {
    return Promise.reject(err)
  }
)

//设置响应拦截器
instance.interceptors.response.use(
  (response: any) => {
    if (response.data) {
      if (response.data.code !== 200 && !(response.data instanceof Blob)) {
        if (!response.config.url.includes('/valid')) {
          MsgError(response.data.message)
          return Promise.reject(response.data)
        }
      }
    }
    return response
  },
  (err: any) => {
    if (err.code === 'ECONNABORTED') {
      MsgError(err.message)
      console.error(err)
    }
    if (err.response?.status === 404) {
      if (!err.response.config.url.includes('/application/authentication')) {
        router.push('/404 ')
      }
    }
    if (err.response?.status === 401) {
      if (
        !err.response.config.url.includes('chat/open') &&
        !err.response.config.url.includes('application/profile')
      ) {
        router.push({ name: 'login' })
      }
    }

    if (err.response?.status === 403 && !err.response.config.url.includes('chat/open')) {
      MsgError(
        err.response.data && err.response.data.message ? err.response.data.message : '没有权限访问'
      )
    }
    return Promise.reject(err)
  }
)

export const request = instance

/* 简化请求方法，统一处理返回结果，并增加loading处理，这里以{success,data,message}格式的返回值为例，具体项目根据实际需求修改 */
const promise: (
  request: Promise<any>,
  loading?: NProgress | Ref<boolean> | WritableComputedRef<boolean>
) => Promise<Result<any>> = (request, loading = ref(false)) => {
  return new Promise((resolve, reject) => {
    if ((loading as NProgress).start) {
      ;(loading as NProgress).start()
    } else {
      ;(loading as Ref).value = true
    }
    request
      .then((response) => {
        // blob类型的返回状态是response.status
        if (response.status === 200) {
          resolve(response?.data || response)
        } else {
          reject(response?.data || response)
        }
      })
      .catch((error) => {
        reject(error)
      })
      .finally(() => {
        if ((loading as NProgress).start) {
          ;(loading as NProgress).done()
        } else {
          ;(loading as Ref).value = false
        }
      })
  })
}

/**
 * 发送get请求   一般用来请求资源
 * @param url    资源url
 * @param params 参数
 * @param loading loading
 * @returns 异步promise对象
 */
export const get: (
  url: string,
  params?: unknown,
  loading?: NProgress | Ref<boolean>,
  timeout?: number
) => Promise<Result<any>> = (
  url: string,
  params: unknown,
  loading?: NProgress | Ref<boolean>,
  timeout?: number
) => {
  return promise(request({ url: url, method: 'get', params, timeout: timeout }), loading)
}

/**
 * faso post请求 一般用来添加资源
 * @param url    资源url
 * @param params 参数
 * @param data   添加数据
 * @param loading loading
 * @returns 异步promise对象
 */
export const post: (
  url: string,
  data?: unknown,
  params?: unknown,
  loading?: NProgress | Ref<boolean>,
  timeout?: number
) => Promise<Result<any> | any> = (url, data, params, loading, timeout) => {
  return promise(request({ url: url, method: 'post', data, params, timeout }), loading)
}

/**|
 * 发送put请求 用于修改服务器资源
 * @param url     资源地址
 * @param params  params参数地址
 * @param data    需要修改的数据
 * @param loading 进度条
 * @returns
 */
export const put: (
  url: string,
  data?: unknown,
  params?: unknown,
  loading?: NProgress | Ref<boolean>,
  timeout?: number
) => Promise<Result<any>> = (url, data, params, loading, timeout) => {
  return promise(request({ url: url, method: 'put', data, params, timeout }), loading)
}

/**
 * 删除
 * @param url     删除url
 * @param params  params参数
 * @param loading 进度条
 * @returns
 */
export const del: (
  url: string,
  params?: unknown,
  data?: unknown,
  loading?: NProgress | Ref<boolean>,
  timeout?: number
) => Promise<Result<any>> = (url, params, data, loading, timeout) => {
  return promise(request({ url: url, method: 'delete', params, data, timeout }), loading)
}

/**
 * 流处理
 * @param url  url地址
 * @param data 请求body
 * @returns
 */
export const postStream: (url: string, data?: unknown) => Promise<Result<any> | any> = (
  url,
  data
) => {
  const { user } = useStore()
  const token = user.getToken()
  const headers: HeadersInit = { 'Content-Type': 'application/json' }
  if (token) {
    headers['AUTHORIZATION'] = `${token}`
  }
  return fetch(url, {
    method: 'POST',
    body: data ? JSON.stringify(data) : undefined,
    headers: headers
  })
}

export const exportExcel: (
  fileName: string,
  url: string,
  params: any,
  loading?: NProgress | Ref<boolean>
) => Promise<any> = (
  fileName: string,
  url: string,
  params: any,
  loading?: NProgress | Ref<boolean>
) => {
  return promise(request({ url: url, method: 'get', params, responseType: 'blob' }), loading)
    .then((res: any) => {
      if (res) {
        const blob = new Blob([res], {
          type: 'application/vnd.ms-excel'
        })
        const link = document.createElement('a')
        link.href = window.URL.createObjectURL(blob)
        link.download = fileName
        link.click()
        //释放内存
        window.URL.revokeObjectURL(link.href)
      }
      return true
    })
    .catch((e) => {})
}

/**
 * 与服务器建立ws链接
 * @param url websocket路径
 * @returns  返回一个websocket实例
 */
export const socket = (url: string) => {
  let protocol = 'ws://'
  if (window.location.protocol === 'https:') {
    protocol = 'wss://'
  }
  let uri = protocol + window.location.host + url
  if (!import.meta.env.DEV) {
    uri = protocol + window.location.host + import.meta.env.VITE_BASE_PATH + url
  }
  return new WebSocket(uri)
}
export default instance
