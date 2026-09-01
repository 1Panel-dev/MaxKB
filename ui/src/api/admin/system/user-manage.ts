import { del, get, getExportFile, post, put } from '../core/request'
import type { ResponsePage, ParamsPage, PasswordRequest } from '../core/types'
import type { Dict, SystemUser, SystemUserPayload, SystemUserUpdateRequest, BatchSetUserRolesRequest, BatchSetUserWorkspaceRolesRequest, ChatUserSyncResult } from '@/api/types'

const prefix = '/user_manage'

/** 获取系统用户分页列表。 */
const getUserManagePage = (page: ParamsPage, query?: Dict<unknown>) => {
  return get<ResponsePage<SystemUser>>(`${prefix}/${page.currentPage}/${page.pageSize}`, query)
}

/** 创建系统用户。 */
const postUser = (payload: SystemUserPayload) => {
  return post<SystemUserPayload, SystemUser>(prefix, payload)
}

/** 编辑系统用户。 */
const putUser = (userId: string, payload: SystemUserUpdateRequest) => {
  return put<SystemUserUpdateRequest, SystemUser>(`${prefix}/${userId}`, payload)
}

/** 修改系统用户密码。 */
const putUserPassword = (userId: string, password: PasswordRequest) => {
  return put<PasswordRequest, boolean>(`${prefix}/${userId}/re_password`, password)
}

/** 删除系统用户。 */
const deleteUser = (userId: string) => {
  return del<boolean>(`${prefix}/${userId}`)
}

/** 批量删除系统用户。 */
const postBatchDeleteUsers = (userIds: string[]) => {
  return post<string[], boolean>(`${prefix}/batch_delete`, userIds)
}

/** 专业版批量设置系统用户角色。 */
const postBatchSetUserRoles = (payload: BatchSetUserRolesRequest) => {
  return post<BatchSetUserRolesRequest, boolean>(`${prefix}/batch/add_role`, payload)
}

/** 企业版批量设置系统用户角色及工作空间。 */
const postBatchSetUserWorkspaceRoles = (payload: BatchSetUserWorkspaceRolesRequest) => {
  return post<BatchSetUserWorkspaceRolesRequest, boolean>(`${prefix}/batch/add_role_ee`, payload)
}


/** 下载系统用户导入模板。 */
const getUserManageImportTemplate = () => {
  return getExportFile('user_import_template.xlsx', `${prefix}/template/export`)
}

/** 获取可导入的系统用户来源。 */
const getUserManageSyncTypes = () => {
  return get<string[]>(`${prefix}/sync/types`)
}

/** 从指定来源同步系统用户（file 来源需携带 xlsx 文件）。 */
const postSyncSystemUsers = (syncType: string, syncFile?: File, workspaceId?: string, roleId?: string, defaultGroupId?: string) => {
  const payload = new FormData()
  if (workspaceId) payload.append('workspace_id', workspaceId)
  if (roleId) payload.append('role_id', roleId)
  if (defaultGroupId) payload.append('default_group_id', defaultGroupId)
  if (syncFile) payload.append('xlsx_file', syncFile)
  return post<FormData, ChatUserSyncResult>(`${prefix}/sync/${syncType}`, payload)
}

export default { deleteUser, getUserManageImportTemplate, getUserManagePage, getUserManageSyncTypes, postUser, postBatchDeleteUsers, postBatchSetUserRoles, postBatchSetUserWorkspaceRoles, postSyncSystemUsers, putUser, putUserPassword }