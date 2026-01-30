import { Result } from '@/request/Result'
import { get, post, del, put, exportFile } from '@/request/index'
import { type Ref } from 'vue'
import type { pageRequest } from '@/api/type/common'
import type { toolData } from '@/api/type/tool'

const prefix = '/system/resource/tool'

/**
 * 工具列表带分页（无分页）
 * @params 参数
 *  param  {
        "name": "string",
        "tool_type": "string",
    }
 */
const getToolList: (data?: any, loading?: Ref<boolean>) => Promise<Result<Array<any>>> = (
  data,
  loading,
) => {
  return get(`${prefix}`, data, loading)
}

/**
 * 工具列表带分页（无分页）
 * @params 参数
 *  param  {
        "name": "string",
        "tool_type": "string",
    }
 */
const getAllToolList: (data?: any, loading?: Ref<boolean>) => Promise<Result<Array<any>>> = (
  data,
  loading,
) => {
  return get(`${prefix}/tool_list`, data, loading)
}

/**
 * 工具列表带分页
 * @param 参数
 * param  {
 "name": "string",
 "tool_type": "string",
 }
 */
const getToolListPage: (
  page: pageRequest,
  param?: any,
  loading?: Ref<boolean>,
) => Promise<Result<any>> = (page, param, loading) => {
  return get(`${prefix}/${page.current_page}/${page.page_size}`, param, loading)
}

/**
 * 获取工具详情
 * @param tool_id 工具id
 * @param loading 加载器
 * @returns 工具详情
 */
const getToolById: (tool_id: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  tool_id,
  loading,
) => {
  return get(`${prefix}/${tool_id}`, undefined, loading)
}


/**
 * 修改工具
 * @param 参数

 */
const putTool: (tool_id: string, data: toolData, loading?: Ref<boolean>) => Promise<Result<any>> = (
  tool_id,
  data,
  loading,
) => {
  return put(`${prefix}/${tool_id}`, data, undefined, loading)
}

const postToolTestConnection: (data: toolData, loading?: Ref<boolean>) => Promise<Result<any>> = (
  data,
  loading,
) => {
  return post(`${prefix}/test_connection`, data, undefined, loading)
}


/**
 * 删除工具
 * @param 参数 tool_id
 */
const delTool: (tool_id: string, loading?: Ref<boolean>) => Promise<Result<boolean>> = (
  tool_id,
  loading,
) => {
  return del(`${prefix}/${tool_id}`, undefined, {}, loading)
}

const putToolIcon: (id: string, data: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  id,
  data,
  loading,
) => {
  return put(`${prefix}/${id}/edit_icon`, data, undefined, loading)
}

const exportTool = (id: string, name: string, loading?: Ref<boolean>) => {
  return exportFile(name + '.tool', `${prefix}/${id}/export`, undefined, loading)
}

/**
 * 调试工具
 * @param 参数

 */
const postToolDebug: (data: any, loading?: Ref<boolean>) => Promise<Result<any>> = (
  data: any,
  loading,
) => {
  return post(`${prefix}/debug`, data, undefined, loading)
}

const postPylint: (code: string, loading?: Ref<boolean>) => Promise<Result<any>> = (
  code,
  loading,
) => {
  return post(`${prefix}/pylint`, { code }, {}, loading)
}

const pageToolRecord = (
  tool_id: string,
  page: pageRequest,
  param: any,
  loading?: Ref<boolean>,
) => {
  return get(
    `${prefix}/${tool_id}/tool_record/${page.current_page}/${page.page_size}`,
    param,
    loading,
  )
}

const getToolRecordDetail = (
 tool_id: string,
 record_id: string
) => {
  return get(`${prefix}/${tool_id}/tool_record/${record_id}`)
}


export default {
  getToolListPage,
  getToolList,
  getAllToolList,
  putTool,
  getToolById,
  postToolDebug,
  postPylint,
  exportTool,
  putToolIcon,
  delTool,
  postToolTestConnection,
  pageToolRecord,
  getToolRecordDetail,
}
