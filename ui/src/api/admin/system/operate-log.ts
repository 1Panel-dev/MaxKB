import { get, post, postBlob } from '../core/request'
import type { ParamsPage, ResponsePage } from '../core/types'
import type { OperateLog, OperateLogMenuOption, OperateLogQuery } from '@/api/types'

const prefix = '/operate_log'

/** 获取操作日志分页列表。 */
const getOperateLogPage = (page: ParamsPage, query: OperateLogQuery) => {
  return get<ResponsePage<OperateLog>>(`${prefix}/${page.currentPage}/${page.pageSize}`, query)
}

/** 获取操作日志菜单筛选项。 */
const getOperateLogMenuOptions = () => {
  return get<OperateLogMenuOption[]>(`${prefix}/menu_operation_option/`)
}

/** 导出符合当前筛选条件的操作日志。 */
const postOperateLogExport = (query: OperateLogQuery) => {
  return postBlob(`${prefix}/export/`, query)
}

/** 保存操作日志自动清理天数。 */
const postOperateLogCleanTime = (cleanTime: number) => {
  return post<{ clean_time: number }, boolean>(`${prefix}/save`, { clean_time: cleanTime })
}

/** 获取操作日志自动清理天数。 */
const getOperateLogCleanTime = () => {
  return get<number>(`${prefix}/get_clean_time`)
}

export default {
  getOperateLogCleanTime,
  getOperateLogMenuOptions,
  getOperateLogPage,
  postOperateLogCleanTime,
  postOperateLogExport,
}
