import { get, post } from '../core/request'
import type { SystemUser, SystemUserQuery } from '@/types'

interface SystemUserPage {
  currentPage: number
  pageSize: number
}

interface PageData<T> {
  total: number
  records: T[]
  current: number
  size: number
}

const prefix = '/user_manage'

/** 获取系统用户分页列表。 */
export function getUserManagePage(page: SystemUserPage, query?: SystemUserQuery) {
  return get<PageData<SystemUser>>(`${prefix}/${page.currentPage}/${page.pageSize}`, query)
}

/** 批量删除系统用户。 */
export function postBatchDeleteUsers(userIds: string[]) {
  return post<void, string[]>(`${prefix}/batch_delete`, userIds)
}

export default {
  getUserManagePage,
  postBatchDeleteUsers,
}
