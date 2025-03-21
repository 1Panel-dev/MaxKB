import { Result } from '@/request/Result'
import { get, exportExcelPost } from '@/request/index'
import type { pageRequest } from '@/api/type/common'
import { type Ref } from 'vue'

const prefix = '/operate_log'
/**
 * 日志分页列表
 * @param 参数 
 * page  {
              "current_page": "string",
              "page_size": "string",
            }
 * @query 参数 
   param: any
 */
const getOperateLog: (
  page: pageRequest,
  param: any,
  loading?: Ref<boolean>
) => Promise<Result<any>> = (page, param, loading) => {
  return get(`${prefix}/${page.current_page}/${page.page_size}`, param, loading)
}

const getMenuList: () => Promise<Result<any>> = () => {
  return get(`${prefix}/menu_operate_option/`, undefined, undefined)
}

const exportOperateLog: (
  param: any,
  loading?: Ref<boolean>
) => void = (param, loading) => {
  exportExcelPost(
    'log.xlsx',
    `${prefix}/export/`,
    param,
    undefined,
    loading
  )
}

export default {
  getOperateLog,
  getMenuList,
  exportOperateLog
}
