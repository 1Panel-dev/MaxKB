import { Result } from '@/request/Result'
import { get, post, del, put } from '@/request/index'
import type { pageRequest } from '@/api/type/common'
import type { functionLibData } from '@/api/type/function-lib'
import { type Ref } from 'vue'

const prefix = '/function_lib'

/**
 * 获取函数列表
 * param {
          "name": "string",
        }
 */
const getAllFunctionLib: (param?: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  param,
  loading
) => {
  return get(`${prefix}`, param || {}, loading)
}

/**
 * 获取分页函数列表
 * page {
          "current_page": "string",
          "page_size": "string",
        }
 * param {
          "name": "string",
        }
 */
const getFunctionLib: (
  page: pageRequest,
  param: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (page, param, loading) => {
  return get(`${prefix}/${page.current_page}/${page.page_size}`, param, loading)
}

/**
 * 创建函数
 * @param 参数
 */
const postFunctionLib: (data: functionLibData, loading?: Ref<boolean>) => Promise<Result<any>> = (
  data,
  loading
) => {
  return post(`${prefix}`, data, undefined, loading)
}

/**
 * 修改函数
 * @param 参数 

 */
const putFunctionLib: (
  function_lib_id: string,
  data: functionLibData,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (function_lib_id, data, loading) => {
  return put(`${prefix}/${function_lib_id}`, data, undefined, loading)
}

/**
 * 调试函数
 * @param 参数 

 */
const postFunctionLibDebug: (data: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  data: any,
  loading
) => {
  return post(`${prefix}/debug`, data, undefined, loading)
}

export default {
  getFunctionLib,
  postFunctionLib,
  putFunctionLib,
  postFunctionLibDebug,
  getAllFunctionLib
}
