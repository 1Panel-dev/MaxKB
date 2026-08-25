import { postExportExcel, get, post } from '../core/request'
import type { ParamsPage, ResponsePage } from '../core/types'
import type { OperateLog, OperateLogMenuOption, RequestParams } from '@/api/types'

const prefix = '/operate_log'

/** 获取操作日志分页列表。 */
const getOperateLogPage = (page: ParamsPage, query: RequestParams) => {
  return get<ResponsePage<OperateLog>>(`${prefix}/${page.currentPage}/${page.pageSize}`, query)
}

/** 获取操作日志菜单筛选项。 */
const getOperateLogMenuOptions = () => {
  return get<OperateLogMenuOption[]>(`${prefix}/menu_operation_option/`)
}

/** 导出操作日志。 */
const exportOperateLog = (query: RequestParams) => {
  return postExportExcel('log.xlsx', `${prefix}/export/`, query)
}

/** 获取对话日志自动清理天数。 */
const getOperateLogCleanTime = () => {
  return get<number>(`${prefix}/get_clean_time`)
}

/** 保存对话日志自动清理天数。 */
const postOperateLogCleanTime = (cleanTime: number) => {
  return post<{ clean_time: number }, boolean>(`${prefix}/save`, { clean_time: cleanTime })
}

export default {
  exportOperateLog,
  getOperateLogCleanTime,
  getOperateLogMenuOptions,
  getOperateLogPage,
  postOperateLogCleanTime,
}
