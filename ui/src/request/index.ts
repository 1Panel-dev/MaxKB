import axios, { type InternalAxiosRequestConfig, AxiosHeaders } from 'axios'
import { MsgError } from '@/utils/message'
import type { NProgress } from 'nprogress'
import type { Ref } from 'vue'
import type { Result } from '@/request/Result'
import useStore from '@/stores'
import router from '@/router'

import { ref, type WritableComputedRef } from 'vue'

const axiosConfig = {
  baseURL: (window.MaxKB?.prefix ? window.MaxKB?.prefix : '/admin') + '/api',
  withCredentials: false,
  timeout: 1800000, // 30分钟 timeout
  headers: {},
}

const instance = axios.create(axiosConfig)

/* 设置请求拦截器 */
instance.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    if (config.headers === undefined) {
      config.headers = new AxiosHeaders()
    }
    if (config.url && config.url.startsWith('http')) {
      return config
    }
    const { user, login } = useStore()
    const token = login.getToken()
    const language = user.getLanguage()
    config.headers['Accept-Language'] = `${language}`
    if (token) {
      config.headers['AUTHORIZATION'] = `Bearer ${token}`
    }
    return config
  },
  (err: any) => {
    return Promise.reject(err)
  },
)

//设置响应拦截器
instance.interceptors.response.use(
  (response: any) => {
    if (response.data) {
      if (response.data.code !== 200 && !(response.data instanceof Blob)) {
        if (response.config.url.includes('/application/authentication')) {
          return Promise.reject(response.data)
        }
        if (
          !response.config.url.includes('/valid') &&
          !response.config.url.includes('/tool/debug')
        ) {
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
        err.response.data && err.response.data.message
          ? err.response.data.message
          : 'No permission to access',
      )
    }
    return Promise.reject(err)
  },
)

export const request = instance

/* 简化请求方法，统一处理返回结果，并增加loading处理，这里以{success,data,message}格式的返回值为例，具体项目根据实际需求修改 */
const promise: (
  request: Promise<any>,
  loading?: NProgress | Ref<boolean> | WritableComputedRef<boolean>,
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
  timeout?: number,
) => Promise<Result<any>> = (
  url: string,
  params: unknown,
  loading?: NProgress | Ref<boolean>,
  timeout?: number,
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
  timeout?: number,
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
  timeout?: number,
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
  timeout?: number,
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
  data,
) => {
  const { user, login } = useStore()
  const token = login.getToken()
  const language = user.getLanguage()
  const headers: HeadersInit = { 'Content-Type': 'application/json' }
  if (token) {
    headers['AUTHORIZATION'] = `Bearer ${token}`
  }
  headers['Accept-Language'] = `${language}`
  return fetch(url, {
    method: 'POST',
    body: data ? JSON.stringify(data) : undefined,
    headers: headers,
  })
}

export const exportExcel: (
  fileName: string,
  url: string,
  params: any,
  loading?: NProgress | Ref<boolean>,
) => Promise<any> = (
  fileName: string,
  url: string,
  params: any,
  loading?: NProgress | Ref<boolean>,
) => {
  return promise(request({ url: url, method: 'get', params, responseType: 'blob' }), loading).then(
    (res: any) => {
      if (res) {
        const blob = new Blob([res], {
          type: 'application/vnd.ms-excel',
        })
        const link = document.createElement('a')
        link.href = window.URL.createObjectURL(blob)
        link.download = fileName
        link.click()
        //释放内存
        window.URL.revokeObjectURL(link.href)
      }
      return true
    },
  )
}

function extractFilename(contentDisposition: string) {
  if (!contentDisposition) return null

  // 处理 URL 编码的文件名
  const urlEncodedMatch =
    contentDisposition.match(/filename=([^;]*)/i) ||
    contentDisposition.match(/filename\*=UTF-8''([^;]*)/i)
  if (urlEncodedMatch && urlEncodedMatch[1]) {
    try {
      return decodeURIComponent(urlEncodedMatch[1].replace(/"/g, ''))
    } catch (e) {
      console.error('解码URL编码文件名失败:', e)
    }
  }

  // 处理 Base64 编码的文件名
  const base64Part = contentDisposition.match(/=\?utf-8\?b\?(.*?)\?=/i)?.[1]
  if (base64Part) {
    try {
      const decoded = decodeURIComponent(escape(atob(base64Part)))
      const filenameMatch = decoded.match(/filename="(.*?)"/i)
      return filenameMatch ? filenameMatch[1] : null
    } catch (e) {
      console.error('解码Base64文件名失败:', e)
    }
  }

  return null
}

export const exportFile: (
  fileName: string,
  url: string,
  params: any,
  loading?: NProgress | Ref<boolean>,
) => Promise<any> = (
  fileName: string,
  url: string,
  params: any,
  loading?: NProgress | Ref<boolean>,
) => {
  return promise(
    request({
      url: url,
      method: 'get',
      params,
      responseType: 'blob',
      transformResponse: [
        function (data, headers) {
          // 在这里可以访问 headers
          if (data.type === 'application/json') {
            data.text().then((text: string) => {
              try {
                const json = JSON.parse(text)
                MsgError(json.message || text)
              } catch {
                MsgError(text)
              }
            })
            throw new Error('Response is not a valid file')
          }
          // const contentType = headers['content-type'];
          const contentDisposition = headers['content-disposition']
          // console.log('Content-Type:', contentType);
          // console.log('Content-Disposition:', contentDisposition);
          // 如果没有提供文件名，则使用默认名称
          fileName = extractFilename(contentDisposition) || fileName
          return data // 必须返回数据
        },
      ],
    }),
    loading,
  )
    .then((res: any) => {
      if (res) {
        const blob = new Blob([res], {
          type: 'application/octet-stream',
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
    .catch(() => {})
}

export const exportExcelPost: (
  fileName: string,
  url: string,
  params: any,
  data: any,
  loading?: NProgress | Ref<boolean>,
) => Promise<any> = (
  fileName: string,
  url: string,
  params: any,
  data: any,
  loading?: NProgress | Ref<boolean>,
) => {
  return promise(
    request({
      url: url,
      method: 'post',
      params, // 查询字符串参数
      data, // 请求体数据
      responseType: 'blob',
    }),
    loading,
  ).then((res: any) => {
    if (res) {
      const blob = new Blob([res], {
        type: 'application/vnd.ms-excel',
      })
      const link = document.createElement('a')
      link.href = window.URL.createObjectURL(blob)
      link.download = fileName
      link.click()
      // 释放内存
      window.URL.revokeObjectURL(link.href)
    }
    return true
  })
}

export const download: (
  url: string,
  method: string,
  data?: any,
  params?: any,
  loading?: NProgress | Ref<boolean>,
) => Promise<any> = (
  url: string,
  method: string,
  data?: any,
  params?: any,
  loading?: NProgress | Ref<boolean>,
) => {
  return promise(request({ url: url, method: method, data, params, responseType: 'blob' }), loading)
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
