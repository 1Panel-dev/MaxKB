import { Result } from '@/request/Result'
import { get, post, del, put, exportFile } from '@/request/index'
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

/**
 * 删除函数
 * @param 参数 function_lib_id
 */
const delFunctionLib: (
  function_lib_id: String,
  loading?: Ref<boolean>
) => Promise<Result<boolean>> = (function_lib_id, loading) => {
  return del(`${prefix}/${function_lib_id}`, undefined, {}, loading)
}
/**
 * 获取函数详情
 * @param function_lib_id 函数id
 * @param loading 加载器
 * @returns 函数详情
 */
const getFunctionLibById: (
  function_lib_id: String,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (function_lib_id, loading) => {
  return get(`${prefix}/${function_lib_id}`, undefined, loading)
}
const pylint: (code: string, loading?: Ref<boolean>) => Promise<Result<any>> = (code, loading) => {
  return post(`${prefix}/pylint`, { code }, {}, loading)
}

const exportFunctionLib = (
  id: string,
  name: string,
  loading?: Ref<boolean>
) => {
  return exportFile(
    name + '.fx',
    `${prefix}/${id}/export`,
    undefined,
    loading
  )
}

const putFunctionLibIcon: (
    id: string,
    data: any,
    loading?: Ref<boolean>
) => Promise<Result<any>> = (id, data, loading) => {
  return put(`${prefix}/${id}/edit_icon`, data, undefined, loading)
}

const addInternalFunction: (
    id: string,
    data: any,
    loading?: Ref<boolean>
) => Promise<Result<any>> = (id, data, loading) => {
  return post(`${prefix}/${id}/add_internal_fun`, data, undefined, loading)
}

const importFunctionLib: (data: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  data,
  loading
) => {
  return post(`${prefix}/import`, data, undefined, loading)
}
export default {
  getFunctionLib,
  postFunctionLib,
  putFunctionLib,
  postFunctionLibDebug,
  getAllFunctionLib,
  delFunctionLib,
  getFunctionLibById,
  exportFunctionLib,
  importFunctionLib,
  pylint,
  putFunctionLibIcon,
  addInternalFunction
}
