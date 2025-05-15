import { Result } from '@/request/Result'
import { get, post, del, put } from '@/request/index'
import { type Ref } from 'vue'
import type { pageRequest } from '@/api/type/common'
import type { toolData } from '@/api/type/tool'
const prefix = '/workspace'

/**
 * 获得工具文件夹列表
 * @params 参数 {folder_id: string}
 */
const getToolByFolder: (
  wordspace_id: string,
  data?: any,
  loading?: Ref<boolean>,
) => Promise<Result<Array<any>>> = (wordspace_id, data, loading) => {
  return get(`${prefix}/${wordspace_id}/tool`, data, loading)
}

/**
 * 工具列表
 * @param 参数
* param  {
              "folder_id": "string",
              "name": "string",
              "tool_type": "string",
            }
 */
const getToolList: (
  wordspace_id: string,
  page: pageRequest,
  param?: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (wordspace_id, page, param, loading) => {
  return get(
    `${prefix}/${wordspace_id}/tool/${page.current_page}/${page.page_size}`,
    param,
    loading,
  )
}

/**
 * 修改工具
 * @param 参数

 */
const putToolLib: (
  wordspace_id: string,
  tool_id: string,
  data: toolData,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (wordspace_id, tool_id, data, loading) => {
  return put(`${prefix}/${wordspace_id}/tool/${tool_id}`, data, undefined, loading)
}

/**
 * 获取工具详情
 * @param tool_id 工具id
 * @param loading 加载器
 * @returns 函数详情
 */
const getToolById: (
  wordspace_id: string,
  tool_id: String,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (wordspace_id, function_lib_id, loading) => {
  return get(`${prefix}/${wordspace_id}/tool/${function_lib_id}`, undefined, loading)
}

export default {
  getToolByFolder,
  getToolList,
  putToolLib,
  getToolById
}
