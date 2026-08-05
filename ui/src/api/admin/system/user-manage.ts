import { get } from '../core/request'
import type { PageData, SystemUser, SystemUserPage, SystemUserQuery } from '@/types'

const prefix = '/user_manage'

/** 获取系统用户分页列表。 */
export function getUserManagePage(page: SystemUserPage, query?: SystemUserQuery) {
  return get<PageData<SystemUser>>(`${prefix}/${page.currentPage}/${page.pageSize}`, query)
}

export default {
  getUserManagePage,
}
