import { del, get, post, put } from '../core/request'
import type { ResponsePage, ParamsPage } from '../core/types'
import type {
  RequestParams,
  SystemUser,
  SystemUserRequest,
  SystemUserPasswordRequest,
} from '@/types'

const prefix = '/user_manage'

/** 获取系统用户分页列表。 */
export function getUserManagePage(page: ParamsPage, query?: RequestParams) {
  return get<ResponsePage<SystemUser>>(`${prefix}/${page.currentPage}/${page.pageSize}`, query)
}

/** 获取默认密码。 */
export function getDefaultPassword() {
  return get<{ password: string }>(`${prefix}/password`)
}

/** 创建系统用户。 */
export function postUser(user: SystemUserRequest) {
  return post<SystemUserRequest, SystemUser>(prefix, user)
}

/** 编辑系统用户。 */
export function putUser(userId: string, user: SystemUserRequest) {
  return put<SystemUserRequest, SystemUser>(`${prefix}/${userId}`, user)
}

/** 修改系统用户密码。 */
export function putUserPassword(userId: string, password: SystemUserPasswordRequest) {
  return put<SystemUserPasswordRequest, boolean>(`${prefix}/${userId}/re_password`, password)
}

/** 删除系统用户。 */
export function deleteUser(userId: string) {
  return del<boolean>(`${prefix}/${userId}`)
}

/** 批量删除系统用户。 */
export function postBatchDeleteUsers(userIds: string[]) {
  return post<string[], boolean>(`${prefix}/batch_delete`, userIds)
}

export default {
  deleteUser,
  getDefaultPassword,
  getUserManagePage,
  postUser,
  postBatchDeleteUsers,
  putUser,
  putUserPassword,
}
